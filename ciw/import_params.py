import copy
import types
import ciw.dists
from .network import *
from .schedules import *
from .routing import *


def create_network(
    arrival_distributions=None,
    baulking_functions=None,
    class_change_matrices=None,
    class_change_time_distributions=None,
    number_of_servers=None,
    priority_classes=None,
    queue_capacities=None,
    service_distributions=None,
    routing=None,
    batching_distributions=None,
    ps_thresholds=None,
    server_priority_functions=None,
    reneging_time_distributions=None,
    service_disciplines=None,
    system_capacity=float('inf')
):
    """
    Takes in kwargs, creates dictionary.
    """
    if (
        arrival_distributions == None
        or number_of_servers == None
        or service_distributions == None
    ):
        raise ValueError(
            "arrival_distributions, service_distributions and number_of_servers are required arguments."
        )

    params = {
        "arrival_distributions": arrival_distributions,
        "number_of_servers": number_of_servers,
        "service_distributions": service_distributions,
        'system_capacity': system_capacity
    }

    if baulking_functions is not None:
        params["baulking_functions"] = baulking_functions
    if class_change_matrices is not None:
        params["class_change_matrices"] = class_change_matrices
    if class_change_time_distributions is not None:
        params["class_change_time_distributions"] = class_change_time_distributions
    if priority_classes is not None:
        params["priority_classes"] = priority_classes
    if queue_capacities is not None:
        params["queue_capacities"] = queue_capacities
    if routing is not None:
        params["routing"] = routing
    if batching_distributions is not None:
        params["batching_distributions"] = batching_distributions
    if ps_thresholds is not None:
        params["ps_thresholds"] = ps_thresholds
    if server_priority_functions is not None:
        params["server_priority_functions"] = server_priority_functions
    if reneging_time_distributions is not None:
        params["reneging_time_distributions"] = reneging_time_distributions
    if service_disciplines is not None:
        params["service_disciplines"] = service_disciplines

    return create_network_from_dictionary(params)


def create_network_from_dictionary(params_input):
    """
    Creates a Network object from a parameters dictionary.
    """
    params = fill_out_dictionary(params_input)
    validify_dictionary(params)
    # Then make the Network object
    number_of_classes = params["number_of_classes"]
    number_of_nodes = params["number_of_nodes"]
    if isinstance(params["priority_classes"], dict):
        preempt_priorities = [False for _ in range(number_of_nodes)]
    if isinstance(params["priority_classes"], tuple):
        preempt_priorities = params["priority_classes"][1]
        params["priority_classes"] = {
            clss: params["priority_classes"][0][clss]
            for clss in params["customer_class_names"]
        }
    class_change_matrices = params.get(
        "class_change_matrices",
        [None for nd in range(number_of_nodes)],
    )
    class_change_time_distributions = {clss2: {clss1: None for clss1 in params['customer_class_names']} for clss2 in params['customer_class_names']}
    if 'class_change_time_distributions' in params:
        for clss1 in params['customer_class_names']:
            for clss2 in params['customer_class_names']:
                try:
                    class_change_time_distributions[clss1][clss2] = params['class_change_time_distributions'][clss1][clss2]
                except:
                    pass

    nodes, classes = [], {}
    for nd in range(number_of_nodes):
        nodes.append(
            ServiceCentre(
                params['number_of_servers'][nd],
                params["queue_capacities"][nd],
                class_change_matrices[nd],
                preempt_priorities[nd],
                params["ps_thresholds"][nd],
                params["server_priority_functions"][nd],
                params["service_disciplines"][nd],
            )
        )
    for clss_name in params['customer_class_names']:
        classes[clss_name] = CustomerClass(
            params['arrival_distributions'][clss_name],
            params['service_distributions'][clss_name],
            params['routing'][clss_name],
            params["priority_classes"][clss_name],
            params["baulking_functions"][clss_name],
            params["batching_distributions"][clss_name],
            params["reneging_time_distributions"][clss_name],
            class_change_time_distributions[clss_name],
        )
    n = Network(nodes, classes)
    n.system_capacity = params['system_capacity']
    return n


def fill_out_dictionary(params):
    """
    Fills out the parameters dictionary with the
    default values of the optional arguments.
    """
    if isinstance(params["arrival_distributions"], list):
        arr_dists = params["arrival_distributions"]
        params["arrival_distributions"] = {"Customer": arr_dists}
    if isinstance(params["service_distributions"], list):
        srv_dists = params["service_distributions"]
        params["service_distributions"] = {"Customer": srv_dists}
    if "routing" in params:
        if isinstance(params["routing"], list):
            transition_matrix = params["routing"]
            params["routing"] = {"Customer": routing.TransitionMatrix(transition_matrix=transition_matrix)}
        elif isinstance(params["routing"], dict):
            for clss in params["routing"]:
                if isinstance(params["routing"][clss], list):
                    transition_matrix = params["routing"][clss]
                    params["routing"][clss] = routing.TransitionMatrix(transition_matrix=transition_matrix)
        else:
            params["routing"] = {"Customer": params["routing"]}
    if "baulking_functions" in params:
        if isinstance(params["baulking_functions"], list):
            blk_fncs = params["baulking_functions"]
            params["baulking_functions"] = {"Customer": blk_fncs}
    if "batching_distributions" in params:
        if isinstance(params["batching_distributions"], list):
            btch_dists = params["batching_distributions"]
            params["batching_distributions"] = {"Customer": btch_dists}
    if "reneging_time_distributions" in params:
        if isinstance(params["reneging_time_distributions"], list):
            reneging_dists = params["reneging_time_distributions"]
            params["reneging_time_distributions"] = {"Customer": reneging_dists}

    class_names = sorted(params["arrival_distributions"].keys())
    params["customer_class_names"] = class_names

    default_dict = {
        "name": "Simulation",
        "routing": {class_name: routing.TransitionMatrix(transition_matrix=[[0.0]]) for class_name in class_names},
        "number_of_nodes": len(params["number_of_servers"]),
        "number_of_classes": len(class_names),
        "queue_capacities": [float("inf") for _ in range(len(params["number_of_servers"]))],
        "priority_classes": {class_name: 0 for class_name in class_names},
        "baulking_functions": {class_name: [None for _ in range(len(params["number_of_servers"]))]for class_name in class_names},
        "batching_distributions": {class_name: [
                ciw.dists.Deterministic(1) for _ in range(len(params["number_of_servers"]))
            ] for class_name in class_names},
        "ps_thresholds": [1 for _ in range(len(params["number_of_servers"]))],
        "server_priority_functions": [
            None for _ in range(len(params["number_of_servers"]))
        ],
        "reneging_time_distributions": {
            class_name: [None for _ in range(len(params["number_of_servers"]))]
            for class_name in class_names
        },
        "service_disciplines": [
            ciw.disciplines.FIFO for _ in range(len(params["number_of_servers"]))
        ],
        "system_capacity": float('inf')
    }

    for a in default_dict:
        params[a] = params.get(a, default_dict[a])
    return params


def validify_dictionary(params):
    """
    Raises errors if there is something wrong with the
    parameters dictionary.
    """
    consistant_num_classes = (
        params["number_of_classes"]
        == len(params["arrival_distributions"])
        == len(params["service_distributions"])
        == len(params["routing"])
        == len(params["batching_distributions"])
        == len(params["reneging_time_distributions"])
    )
    if not consistant_num_classes:
        raise ValueError("Ensure consistant number of classes is used throughout.")
    consistant_class_names = (
        set(params["arrival_distributions"])
        == set(params["service_distributions"])
        == set(params["routing"])
        == set(params["batching_distributions"])
        == set(params["reneging_time_distributions"])
    ) and (
        len(params["arrival_distributions"])
        == len(params["service_distributions"])
        == len(params["batching_distributions"])
        == len(params["reneging_time_distributions"])
    )
    if not consistant_class_names:
        raise ValueError("Ensure consistant names for customer classes.")
    num_nodes_count = (
        [params["number_of_nodes"]]
        + [len(obs) for obs in params["arrival_distributions"].values()]
        + [len(obs) for obs in params["service_distributions"].values()]
        + [len(obs) for obs in params["batching_distributions"].values()]
        + [len(obs) for obs in params["reneging_time_distributions"].values()]
        + [len(params["number_of_servers"])]
        + [len(params["server_priority_functions"])]
        + [len(params["queue_capacities"])]
    )
    if len(set(num_nodes_count)) != 1:
        raise ValueError("Ensure consistant number of nodes is used throughout.")
    neg_numservers = any(
        [(isinstance(obs, int) and obs < 0) for obs in params["number_of_servers"]]
    )
    valid_capacities = all(
        [
            ((isinstance(obs, int) and obs >= 0) or obs == float("inf") or obs == "Inf")
            for obs in params["queue_capacities"]
        ]
    )
    if neg_numservers:
        raise ValueError("Number of servers must be positive integers.")
    for c in params["number_of_servers"]:
        if not (isinstance(c, int) or isinstance(c, Schedule) or c == float('inf')):
            raise ValueError("Number of servers must be positive integers or instances of ciw.schedules.Schedule.")
    if not valid_capacities:
        raise ValueError("Queue capacities must be positive integers or zero.")
    
    if "class_change_matrices" in params:
        if not isinstance(params['class_change_matrices'], list):
            raise ValueError("class_change_matrices should be a list of dictionaries for each node in the network.")
        num_nodes = len(params["class_change_matrices"]) == params["number_of_nodes"]
        if not num_nodes:
            raise ValueError("Ensure correct nodes used in class_change_matrices.")
        for nd in params["class_change_matrices"]:
            for row in nd.values():
                if sum(row.values()) > 1.0 or min(row.values()) < 0.0 or max(row.values()) > 1.0:
                    raise ValueError("Ensure that class change matrix is valid.")
        class_change_names = set([k for matrix in params['class_change_matrices'] for k in matrix.keys()])
        if not class_change_names.issubset(set(params['arrival_distributions'])):
            raise ValueError("Ensure consistant names for customer classes.")
    
    if "class_change_time_distributions" in params:
        class_change_from_names = set(list(params['class_change_time_distributions'].keys()))
        class_change_to_names = set([clss for row in params['class_change_time_distributions'].values() for clss in row.keys()])
        wrong_class_names = (
            not class_change_from_names.issubset(set(params['customer_class_names']))
        ) or (
        
            not class_change_to_names.issubset(set(params['customer_class_names']))
        )
        if wrong_class_names:
            raise ValueError(
                "Ensure consistant customer classes used in class_change_time_distributions."
            )

    if not isinstance(params['system_capacity'], int) and params['system_capacity'] != float('inf'):
        raise ValueError("Ensure system capacity is a positive integer.")
    if params['system_capacity'] <= 0:
        raise ValueError("Ensure system capacity is a positive integer.")
