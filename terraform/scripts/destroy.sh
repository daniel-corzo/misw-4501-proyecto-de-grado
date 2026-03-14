#!/bin/bash

export AWS_PROFILE=travelhub
printf "AWS_PROFILE: %s\n\n" "$AWS_PROFILE"

set -e

PROJECT_ROOT=$(pwd)
ENV="travelhub"

source "$PROJECT_ROOT/terraform/scripts/stacks.sh"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_stack_header() {
  printf "%b" "${RED}"
  printf "==============================================\n"
  printf "DESTROY STACK: %s\n" "$1"
  printf "==============================================\n"
  printf "%b\n" "${NC}"
}

print_step() {
  printf "%b➜ %s%b\n" "${CYAN}" "$1" "${NC}"
}

print_success() {  
  printf "%b✔ %s%b\n\n" "${GREEN}" "$1" "${NC}"
}

printf "%b\n" "${YELLOW}⚠️  Destroying Terraform infrastructure${NC}"

for (( idx=${#STACKS[@]}-1 ; idx>=0 ; idx-- )) ; do

  STACK=${STACKS[idx]}

  print_stack_header "$STACK"

  TF_DIR="$PROJECT_ROOT/terraform/stacks/$STACK"
  ENV_DIR="$PROJECT_ROOT/terraform/environments/$ENV/$STACK"

  print_step "Destroying infrastructure"
  terraform -chdir="$TF_DIR" destroy \
    -var-file="$ENV_DIR/terraform.tfvars" \
    -auto-approve

  print_success "Stack $STACK destroyed"

done

printf "%b" "${GREEN}"
printf "==============================================\n"
printf "All stacks destroyed\n"
printf "==============================================\n"
printf "%b" "${NC}"
