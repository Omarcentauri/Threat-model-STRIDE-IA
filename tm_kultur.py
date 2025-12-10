#!/usr/bin/env python3
from pytm.pytm import TM, Server, Datastore, Dataflow, Boundary, Actor

tm = TM("Kultur Process Threat Model")
tm.description = "Modelo de amenazas para Kultur Process (STRIDE + PyTM)"
tm.isOrdered = True

user_web = Boundary("User/Web")
api_boundary = Boundary("Kultur Process API")
evidence_boundary = Boundary("Evidence Automation")

user = Actor("User (Web/SPA Admin/Operadores)")
user.inBoundary = user_web

providers = Actor("Providers Service (MS_PROVIDERS_URL)")

api = Server("ApiRouter (Routes & Controllers)")
api.inBoundary = api_boundary
api.OS = "Linux"
api.isHardened = False
api.implementsAuthenticationScheme = True

clients_svc = Server("Clients Service (MS_CLIENTS_URL)")
clients_svc.inBoundary = api_boundary

services = Server("Services & Jobs (lógica de dominio)")
services.inBoundary = api_boundary
services.handlesResources = True

repos = Server("Repositories & Models")
repos.inBoundary = api_boundary

db = Datastore("DB MySQL (kultur_process)")
db.inBoundary = api_boundary
db.isSql = True
db.storesPersonalData = True
db.isEncrypted = False

s3 = Datastore("S3 Storage (evidencias, reportes)")
s3.inBoundary = api_boundary
s3.storesLogs = True
s3.isEncrypted = False

queue = Datastore("DB Queue (Supervisor workers)")
queue.inBoundary = api_boundary
queue.isSql = True
queue.storesLogs = True

scheduler = Server("Laravel Scheduler")
scheduler.inBoundary = evidence_boundary

auto_job = Server("AutomatedEvdCollectionJob")
auto_job.inBoundary = evidence_boundary

evidence_svc = Server("EvidenceCollectionService")
evidence_svc.inBoundary = evidence_boundary
evidence_svc.handlesResources = True

exec_job = Server("ExecuteEndpointRequestJob")
exec_job.inBoundary = evidence_boundary

upload_svc = Server("UploadEvidenceService / StoreResourceService")
upload_svc.inBoundary = evidence_boundary
upload_svc.handlesResources = True

user_to_api = Dataflow(user, api, "HTTPS API (auth/login/roles)")
user_to_api.protocol = "HTTPS"
user_to_api.dstPort = 443
user_to_api.data = "Credenciales, JWT, solicitudes de procesos"

api_to_clients = Dataflow(api, clients_svc, "Consultas de clientes")
api_to_clients.protocol = "HTTP"

api_to_services = Dataflow(api, services, "Operaciones de procesos / reportes")
api_to_services.protocol = "HTTP"

services_to_repos = Dataflow(services, repos, "Lógica de dominio → repos")
services_to_repos.protocol = "PHP-internal"

repos_to_db = Dataflow(repos, db, "Consultas de dominio")
repos_to_db.protocol = "SQL"
repos_to_db.dstPort = 3306

services_to_s3 = Dataflow(services, s3, "Subir evidencias / reportes")
services_to_s3.protocol = "HTTPS"

services_to_queue = Dataflow(services, queue, "Encolar tareas de Supervisor")
services_to_queue.protocol = "SQL"

scheduler_to_autojob = Dataflow(scheduler, auto_job, "run: automated-evd-collection")
scheduler_to_autojob.protocol = "internal"

autojob_to_evidence = Dataflow(auto_job, evidence_svc, "Inicializar recolección")
autojob_to_evidence.protocol = "internal"

evidence_to_execjob = Dataflow(evidence_svc, exec_job, "queue: QUEUE_EVIDENCES")
evidence_to_execjob.protocol = "internal"

evidence_to_db = Dataflow(evidence_svc, db, "Registrar estado de evidencia")
evidence_to_db.protocol = "SQL"

execjob_to_providers = Dataflow(exec_job, providers, "Llamar APIs externas de proveedores")
execjob_to_providers.protocol = "HTTPS"

execjob_to_upload = Dataflow(exec_job, upload_svc, "Procesar evidencia descargada")
execjob_to_upload.protocol = "internal"

upload_to_s3 = Dataflow(upload_svc, s3, "Subir archivos de evidencia")
upload_to_s3.protocol = "HTTPS"

upload_to_db = Dataflow(upload_svc, db, "Guardar metadatos de evidencia")
upload_to_db.protocol = "SQL"

if __name__ == "__main__":
    tm.process()
