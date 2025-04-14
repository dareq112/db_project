#Tutaj deklarujesz, jakie dane będą zmienne w konfiguracji.
#Możesz potem je ustawiać dynamicznie w terraform.tfvars.
#Jeśli widzisz klamry {} w pliku variables.tf, to są to domyślne wartości zmiennych, które są przypisane bezpośrednio w definicji zmiennej.

variable "project_id" {}
variable "region" { default = "europe-central2" }
variable "credentials_file" {}
variable "bucket_name" {}
variable "dataset_id" {}
variable "cluster_name" {}
