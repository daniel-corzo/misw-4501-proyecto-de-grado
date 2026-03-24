#!/bin/bash
# Destruye los stacks que generan costo mientras la infra no está en uso.
# Conserva: network, ecr, static-frontend, cloudfront  (costo ~$0)
# Destruye:  cicd-frontend, cicd-backend, ecs, alb, rds (~$98/mes)
#
# Uso: ejecutar desde src/
#   cd src && bash infrastructure/terraform/scripts/teardown.sh

export AWS_PROFILE=travelhub
printf "AWS_PROFILE: %s\n\n" "$AWS_PROFILE"

set -e

PROJECT_ROOT=$(pwd)
ENV="travelhub"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TEARDOWN_STACKS=(
  cicd-frontend
  cicd-backend
  ecs
  alb
  rds
)

print_stack_header() {
  printf "%b" "${RED}"
  printf "==============================================\n"
  printf "TEARDOWN STACK: %s\n" "$1"
  printf "==============================================\n"
  printf "%b\n" "${NC}"
}

print_step() {
  printf "%b➜ %s%b\n" "${CYAN}" "$1" "${NC}"
}

print_success() {
  printf "%b✔ %s%b\n\n" "${GREEN}" "$1" "${NC}"
}

TOTAL_STACKS=${#TEARDOWN_STACKS[@]}
current=0

printf "%b\n" "${YELLOW}⚠️  Teardown: destruyendo stacks con costo (conservando network, ecr, static-frontend, cloudfront)${NC}"
printf "%bProgress: 0/%d stacks%b\n\n" "${CYAN}" "$TOTAL_STACKS" "${NC}"

for STACK in "${TEARDOWN_STACKS[@]}"; do
  current=$((current + 1))
  printf "%bProgress: [%d/%d] %s%b\n" "${CYAN}" "$current" "$TOTAL_STACKS" "$STACK" "${NC}"

  print_stack_header "$STACK"

  TF_DIR="$PROJECT_ROOT/infrastructure/terraform/stacks/$STACK"
  ENV_DIR="$PROJECT_ROOT/infrastructure/terraform/environments/$ENV/$STACK"

  print_step "Initializing backend"
  terraform -chdir="$TF_DIR" init \
    -backend-config="$ENV_DIR/backend.tfvars" \
    -reconfigure

  print_step "Destroying infrastructure"
  terraform -chdir="$TF_DIR" destroy \
    -var-file="$ENV_DIR/terraform.tfvars" \
    -auto-approve

  printf "%bProgress: [%d/%d] %s ✔%b\n" "${GREEN}" "$current" "$TOTAL_STACKS" "$STACK" "${NC}"
  print_success "Stack $STACK destruido"

done

printf "%b" "${GREEN}"
printf "==============================================\n"
printf "Teardown completado. Stacks destruidos:\n"
for s in "${TEARDOWN_STACKS[@]}"; do printf "  - %s\n" "$s"; done
printf "\nStacks conservados (costo ~\$0):\n"
printf "  - network\n  - ecr\n  - static-frontend\n  - cloudfront\n"
printf "==============================================\n"
printf "%b" "${NC}"
