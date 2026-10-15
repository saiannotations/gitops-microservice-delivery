{{- define "orders-api.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "orders-api.fullname" -}}
{{- printf "%s-%s" (include "orders-api.name" .) (.Values.environment | default "dev") | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "orders-api.labels" -}}
app.kubernetes.io/name: {{ include "orders-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
environment: {{ .Values.environment | default "dev" | quote }}
{{- end -}}
