variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "Central US"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "musicai"
}

variable "env" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8080
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    Environment = "dev"
    Project     = "musicAI"
    ManagedBy   = "terraform"
  }
}
