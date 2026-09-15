{
	"package": "TVRAPatientsMonitoring",
	"classes": [
	  { "name": "Patient", "stereotype": "Person" },
	  { "name": "Patients_Phone" },
	  { "name": "Sensor_App" },
	  { "name": "Sensor" },
	  { "name": "Public" },
	  { "name": "Patients_Work" },
	  { "name": "Patients_House" },
	  { "name": "Patients_Wifi" },
	  { "name": "Patients_Router" }
	],
	"relationships": [
	  {
		"source": "Patients_Phone",
		"target": "Patient",
		"label": "manages",
		"sourceRole": "patients phone",
		"targetRole": "patient",
		"direction": "<--"
	  },
	  {
		"source": "Sensor",
		"target": "Patient",
		"label": "relatesTo",
		"sourceRole": "sensor",
		"targetRole": "patient",
		"direction": "-->"
	  },
	  {
		"source": "Sensor_App",
		"target": "Patient",
		"label": "interactsWith",
		"sourceRole": "sensor app",
		"targetRole": "patient",
		"direction": "<--"
	  },
	  {
		"source": "Sensor_App",
		"target": "Patients_Phone",
		"label": "hosts",
		"sourceRole": "sensor app",
		"targetRole": "patients phone",
		"direction": "<--"
	  },
	  {
		"source": "Sensor",
		"target": "Patients_Phone",
		"label": "pairsViaBluetooth",
		"sourceRole": "sensor",
		"targetRole": "patients phone",
		"direction": "<--"
	  },
	  {
		"source": "Public",
		"target": "Patients_Phone",
		"label": "locatedIn",
		"sourceRole": "public",
		"targetRole": "patients phone",
		"direction": "<--"
	  },
	  {
		"source": "Patients_Work",
		"target": "Patients_Phone",
		"label": "locatedIn",
		"sourceRole": "patients work",
		"targetRole": "patients phone",
		"direction": "<--"
	  },
	  {
		"source": "Patients_Phone",
		"target": "Patients_House",
		"label": "locatedIn",
		"sourceRole": "patients phone",
		"targetRole": "patients house",
		"direction": "-->"
	  },
	  {
		"source": "Patients_Phone",
		"target": "Patients_Wifi",
		"label": "connectedTo",
		"sourceRole": "patients phone",
		"targetRole": "patients wifi",
		"direction": "-->"
	  },
	  {
		"source": "Patients_Router",
		"target": "Patients_Wifi",
		"label": "providedBy",
		"sourceRole": "patients router",
		"targetRole": "patients wifi",
		"direction": "<--"
	  },
	  {
		"source": "Sensor",
		"target": "Sensor_App",
		"direction": "<--"
	  }
	]
  }
  