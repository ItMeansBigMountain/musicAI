output "container_app_fqdn" {
  description = "Container App FQDN"
  value       = azurerm_container_app.app.latest_revision_fqdn
}

output "container_app_name" {
  description = "Container App name"
  value       = azurerm_container_app.app.name
}

output "acr_login_server" {
  description = "ACR login server"
  value       = azurerm_container_registry.acr.login_server
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}
