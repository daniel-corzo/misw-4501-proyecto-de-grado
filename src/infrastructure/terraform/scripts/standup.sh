#!/bin/bash
# Recrea los stacks destruidos por teardown.sh.
# Asume que network, ecr, static-frontend y cloudfront siguen existiendo.
#
# Uso: ejecutar desde src/
#   cd src && bash infrastructure/terraform/scripts/standup.sh

export AWS_PROFILE=travelhub
printf "AWS_PROFILE: %s\n\n" "$AWS_PROFILE"

set -e

PROJECT_ROOT=$(pwd)
ENV="travelhub"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

STANDUP_STACKS=(
  rds
  alb
  ecs
  cicd-backend
  cicd-frontend
)

print_stack_header() {
  printf "%b" "${BLUE}"
  printf "==============================================\n"
  printf "STANDUP STACK: %s\n" "$1"
  printf "==============================================\n"
  printf "%b\n" "${NC}"
}

print_step() {
  printf "%b➜ %s%b\n" "${CYAN}" "$1" "${NC}"
}

print_success() {
  printf "%b✔ %s%b\n\n" "${GREEN}" "$1" "${NC}"
}

TOTAL_STACKS=${#STANDUP_STACKS[@]}
current=0

printf "%b\n" "${YELLOW}🚀 Standup: recreando stacks (rds → alb → ecs → cicd-backend → cicd-frontend)${NC}"
printf "%bProgress: 0/%d stacks%b\n\n" "${CYAN}" "$TOTAL_STACKS" "${NC}"

for STACK in "${STANDUP_STACKS[@]}"; do
  current=$((current + 1))
  printf "%bProgress: [%d/%d] %s%b\n" "${CYAN}" "$current" "$TOTAL_STACKS" "$STACK" "${NC}"

  print_stack_header "$STACK"

  TF_DIR="$PROJECT_ROOT/infrastructure/terraform/stacks/$STACK"
  ENV_DIR="$PROJECT_ROOT/infrastructure/terraform/environments/$ENV/$STACK"

  print_step "Initializing Terraform"
  terraform -chdir="$TF_DIR" init \
    -backend-config="$ENV_DIR/backend.tfvars" \
    -reconfigure

  print_step "Validating configuration"
  terraform -chdir="$TF_DIR" validate

  print_step "Generating execution plan"
  terraform -chdir="$TF_DIR" plan \
    -var-file="$ENV_DIR/terraform.tfvars" \
    -out=.tfplan

  print_step "Applying infrastructure"
  terraform -chdir="$TF_DIR" apply .tfplan

  printf "%bProgress: [%d/%d] %s ✔%b\n" "${GREEN}" "$current" "$TOTAL_STACKS" "$STACK" "${NC}"
  print_success "Stack $STACK levantado"

done

printf "%b" "${GREEN}"
printf "==============================================\n"
printf "Standup completado. Stacks recreados:\n"
for s in "${STANDUP_STACKS[@]}"; do printf "  - %s\n" "$s"; done
printf "==============================================\n"
printf "%b" "${NC}"
