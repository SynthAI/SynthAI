BeginPackage["LabEnvironment`", {"GeneralUtilities`"}]

EnvCreate;
EnvClose;
EnvListAll;
EnvReset;
EnvStep;

EnvActionSpaceInfo;
EnvActionSpaceSample;
EnvActionSpaceContains;
EnvObservationSpaceInfo;

EnvMonitorStart;
EnvMonitorClose;

ShutdownLabServer;

LabEnvironmentObject;

LabUpload;

Begin["`Private`"]

$DefaultServer = "http://127.0.0.1:5000";

(*----------------------------------------------------------------------------*)
(* Private functions *)

(*************************)
(* Factor out the commmon error handling routine *)

$unknownError = Failure["UnknownError", <|"MessageTemplate" :> "Error of unknown type."|>]; 

labSafeRequestExecute[req_HTTPRequest] := Module[
	{res, body, msg},
	res = Quiet @ URLRead[req];
	If[FailureQ[res], Throw[res]];
	body = Quiet @ Developer`ReadRawJSONString[res["Body"]];
	(* sometimes, the body is a string that is not JSONizable, eg
		\"Server shutting down\". Need to handle this case.  *)
	msg = If[FailureQ[body], Missing[], Lookup[body, "message"]];
	If[(res["StatusCode"] =!= 200) && !MissingQ[msg],
		Throw @ Failure["ServerError", <|
			"MessageTemplate" :> StringTemplate["`Message`"], 
			"MessageParameters" -> <|"Message" -> msg|>
		|>]
	];
	body
]

labSafeRequestExecute[_] := Throw[$unknownError]

(*************************)

labPOSTRequest[server_String, route_String, data_Association] := labSafeRequestExecute[
	HTTPRequest[server <> route, 
		<|
			"Body" -> Developer`WriteRawJSONString[data],
			Method -> "POST",
			"ContentType" -> "application/json"
		|>
	]
]

labPOSTRequest[server_String, route_String] := labPOSTRequest[server, route, <||>]


labGETRequest[server_String, route_String] := labSafeRequestExecute[
	HTTPRequest[server <> route, 
		<|
			Method -> "GET",
			"ContentType" -> "application/json"
		|>
	]
]

(*************************)
(* Make LabEnvironmentObject objects format nicely in notebooks *)

DefineCustomBoxes[LabEnvironmentObject, 
	e:LabEnvironmentObject[id_, name_, server_] :> Block[
	{},
	BoxForm`ArrangeSummaryBox[
		LabEnvironmentObject, e, 
		None, 
		{BoxForm`SummaryItem[{"ID: ", id}]
		 },
		{},
		StandardForm
	]]
];

(*----------------------------------------------------------------------------*)
(* Start of public API *)

(*************************)
SetUsage["
LabEnvironmentObject[id$]['ID'] returns the ID of the environment.
LabEnvironmentObject[id$]['Name'] returns the name of the environment.
LabEnvironmentObject[id$]['URL'] returns the URL of the server the environment \
is running on.
"]

LabEnvironmentObject[id_, _, _]["ID"] := id
LabEnvironmentObject[_, name_, _]["Name"] := name	
LabEnvironmentObject[_, _, url_]["URL"] := url	

(*************************)
SetUsage["
EnvListAll[] lists all environments running on the default server.
EnvListAll[url$] lists environments given the specified server url$, where url$ is \
either a string or a URL object.
"]

EnvListAll[server_String] := Catch @ Module[
	{res},
	res = labGETRequest[server, "/v1/envs/"];
	res["all_envs"]
]

EnvListAll[URL[server]] := EnvListAll[server]
EnvListAll[] := EnvListAll[$DefaultServer];

(*************************)
SetUsage["
EnvCreate[type$] creates an instance of the environment with string \
name type$ on the default server.
EnvCreate[type$, url$] creates an environment on the specified server url$, \
where url$ is either a string or a URL object.
"]

EnvCreate[type_String, server_String] := Catch @ Module[
	{res},
	res = labPOSTRequest[server, "/v1/envs/", <|"env_id" -> type|>];
	LabEnvironmentObject[res["instance_id"], type, server]
]

EnvCreate[type_String, URL[server_]] := 
	EnvCreate[type, server]

EnvCreate[type_String] :=
	EnvCreate[type, $DefaultServer]

(*************************)
SetUsage["
EnvClose[LabEnvironmentObject[id$]] closes the environment..
"]

EnvClose[ins_LabEnvironmentObject] := Catch @ Module[{},
	labPOSTRequest[ins["URL"], StringJoin["/v1/envs/", ins["ID"], "/close/"]];
]

(*************************)	
SetUsage["
EnvStep[LabEnvironmentObject[id$], act$] steps through an environment using \
an action act$. EnvReset[LabEnvironmentObject[id$]] must be called before the first \
call to EnvStep. 
EnvStep[LabEnvironmentObject[id$], act$, render$] displays the current state \
of the environment in a separate windows when render$ is True.
"]

EnvStep[ins_LabEnvironmentObject, action_, render_:False] := Catch @ Module[
	{route, data},
	route = StringJoin["/v1/envs/", ins["ID"], "/step/"];	
	data = <|"action" -> action, "render" -> render|>;
	labPOSTRequest[ins["URL"], route, data]
]

(*************************)	
SetUsage["
EnvReset[LabEnvironmentObject[id$]] resets the state of the environment and \
returns an initial observation.
"]
	
EnvReset[ins_LabEnvironmentObject] := Catch @ Module[
	{route, res},
	route = StringJoin["/v1/envs/", ins["ID"], "/reset/"];
	res = labPOSTRequest[ins["URL"], route];
	res["observation"]
]

(*************************)
SetUsage["
EnvActionSpaceInfo[LabEnvironmentObject[id$]] returns an Association \
containing information (name and dimensions/bounds) of the environment's action space.
"]

EnvActionSpaceInfo[ins_LabEnvironmentObject] := Catch @ Module[
	{route, res},
	route = StringJoin["/v1/envs/", ins["ID"], "/action_space/"];
	res = labGETRequest[ins["URL"], route];
	res["info"]
]

(*************************)
SetUsage["
EnvActionSpaceSample[LabEnvironmentObject[id$]] randomly samples an \
action from the action space.
"]

EnvActionSpaceSample[ins_LabEnvironmentObject] := Catch @ Module[
	{route, res},
	route = StringJoin["/v1/envs/", ins["ID"], "/action_space/sample"];
	res = labGETRequest[ins["URL"], route];
	res["action"]
]

(*************************)
SetUsage["
EnvActionSpaceContains[LabEnvironmentObject[id$], act$] returns True if act$ is \
an element of the action space, otherwise False.
"]

EnvActionSpaceContains[ins_LabEnvironmentObject, act_] := Catch @ Module[
	{route, res},
	route = StringJoin["/v1/envs/", ins["ID"], "/action_space/contains/", ToString[act]];
	res = labGETRequest[ins["URL"], route];
	res["member"]
]

(*************************)
SetUsage["
EnvObservationSpaceInfo[LabEnvironmentObject[id$]] gets information \
(name and dimensions/bounds) of the environments observation space.
"]

EnvObservationSpaceInfo[ins_LabEnvironmentObject] := Catch @ Module[
	{route, res},
	route = StringJoin["/v1/envs/", ins["ID"], "/observation_space/"];
	res = labGETRequest[ins["URL"], route];
	res["info"]
]

(*************************)
SetUsage["
EnvMonitorStart[LabEnvironmentObject[id$], dir$] starts logging actions and \
environment states to a file stored in dir$. The following options are available: 
| 'Force' | False | Clear out existing training data from this directory \
(by deleting every file prefixed with 'synthailab.') |
| 'Resume' | False | Retain the training data already in this directory, \
which will be merged with our new data. |
| 'VideoCallable' | False | Not yet implemented. |
"]

Options[EnvMonitorStart] =
{
	"Force" -> False,
	"Resume" -> False,
	"VideoCallable" -> False
};

EnvMonitorStart[ins_LabEnvironmentObject, dir_, opts:OptionsPattern[]] := Catch @ Module[
	{route, data},
	data = <|
		"directory" -> If[Head[dir] === File, First[dir], dir],
		"force" -> OptionValue["Force"],
		"resume" -> OptionValue["Resume"],
		"video_callable" -> OptionValue["VideoCallable"]
	|>;
	route = StringJoin["/v1/envs/", ins["ID"], "/monitor/start/"];	
	labPOSTRequest[ins["URL"], route, data]; (* don't return *)
]

(*************************)
SetUsage["
EnvMonitorClose[LabEnvironmentObject[id$]] flushes all monitor data to disk.
"]

EnvMonitorClose[ins_LabEnvironmentObject] := Catch @ Module[{},
	labPOSTRequest[ins["URL"], StringJoin["/v1/envs/", ins["ID"], "/monitor/close/"]];
]

(*************************)
SetUsage["
LabUpload[dir$] uploads results stored in dir$ to SynthAI Lab Server. Uses default \
server URL.
LabUpload[dir$, url$] uploads given a user-defined server url$.
| 'AlgorithmID' | '' | Name of algorithm |
| 'APIKey' | Automatic | When Automatic, tries to obtain key using GetEnvironment. \
otherwise, need to specify the key. |
"]

Options[LabUpload] =
{
	"AlgorithmID" -> "",
	"APIKey" -> Automatic
};

LabUpload[dir_String, url_String, opts:OptionsPattern[]] := Catch @ Module[
	{data, apiKey = OptionValue["APIKey"]},
	apiKey = If[apiKey === Automatic, 
		Values @ GetEnvironment["SYNTHAI_LAB_API_KEY"]
	];
	If[apiKey === None, 
		Throw @ Failure["LabAPIKey", <|"MessageTemplate" :> "No Lab API key defined."|>]
	];
	data = <|
		"training_dir" -> If[Head[dir] === File, First[dir], dir], 
		"algorithm_id" -> OptionValue["AlgorithmID"],
		"api_key" -> apiKey
	|>;
	labPOSTRequest[url, "/v1/upload/", data]; (* don't return *)
]

LabUpload[dir_String, URL[url_], opts:OptionsPattern[]] := LabUpload[dir, url, opts]
LabUpload[dir_String, opts:OptionsPattern[]] := LabUpload[dir, $DefaultServer, opts]

(*************************)
SetUsage["
ShutdownLabServer[] requests a server shutdown at the default server URL.
ShutdownLabServer[url$] requests a shutdown of a server at the address url$, \
where url$ is either a string or URL object.
"]

ShutdownLabServer[url_String] := Catch @ Module[{},
	labPOSTRequest[url, "/v1/shutdown/"];
]

ShutdownLabServer[URL[url_]] := ShutdownLabServer[url]
ShutdownLabServer[] := ShutdownLabServer[$DefaultServer]

(*----------------------------------------------------------------------------*)

End[ ]

EndPackage[ ]