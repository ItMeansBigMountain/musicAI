# Simple Terraform for basic container app

terraform {
  required_version = ">= 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group - dedicated name like your example
resource "azurerm_resource_group" "main" {
  name     = "musicai-rg"
  location = var.azure_location
  tags     = var.tags
}

# Container Registry
resource "azurerm_container_registry" "acr" {
  name                = "${var.app_name}acr${var.env}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = var.tags
}

# Container Apps Environment
resource "azurerm_container_app_environment" "cae" {
  name                       = "cae-${var.app_name}-${var.env}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tags                       = var.tags
}

# Container App
resource "azurerm_container_app" "app" {
  name                         = "ca-${var.app_name}-${var.env}"
  container_app_environment_id = azurerm_container_app_environment.cae.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = var.tags

  template {
    container {
      name   = var.app_name
      image  = "${azurerm_container_registry.acr.login_server}/${var.app_name}:${var.image_tag}"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "PORT"
        value = var.container_port
      }
    }

    min_replicas = 0
    max_replicas = 1
  }

  ingress {
    external_enabled = true
    target_port     = var.container_port
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}
