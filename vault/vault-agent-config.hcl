pid_file = "/tmp/vault-agent.pid"

auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/etc/vault/role_id"
      secret_id_file_path = "/etc/vault/secret_id"
    }
  }

  sink "file" {
    config = {
      path = "/etc/secrets/gemini_api_key"
    }
  }
}

template {
  destination = "/etc/secrets/gemini_api_key"
  content = "{{ with secret \"secret/data/gemini\" }}{{ .Data.data.gemini_api_key }}{{ end }}"
}
