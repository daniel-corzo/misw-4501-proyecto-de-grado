# TravelHub

## Terraform

Para correr los scripts de Terraform, primero se debe configurar el perfil de AWS.

```bash
aws configure --profile travelhub
```

> [!IMPORTANT]
> El perfil de AWS debe llamarse `travelhub`, para que los scripts de Terraform funcionen correctamente.

Luego, se pueden correr los scripts de Terraform.

```bash
./infrastructure/terraform/scripts/apply.sh
```

Para destruir la infraestructura, se puede correr el siguiente script.

```bash
./infrastructure/terraform/scripts/destroy.sh
```
