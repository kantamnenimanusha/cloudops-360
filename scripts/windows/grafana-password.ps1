# Prints the auto-generated Grafana admin password (stored in a Kubernetes Secret, never in Git).
$b64 = kubectl -n monitoring get secret kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}'
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b64))
