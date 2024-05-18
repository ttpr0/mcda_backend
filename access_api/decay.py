import pyaccess

def get_distance_decay(param: dict) -> pyaccess._pyaccess_ext.IDistanceDecay | None:
    try:
        match param["decay_type"]:
            case "hybrid":
                if "ranges" not in param or "range_factors" not in param:
                    return None
                if len(param["ranges"]) == 0 or len(param["range_factors"]) != len(param["ranges"]):
                    return None
                return pyaccess.hybrid_decay([int(i) for i in param["ranges"]], [float(i) for i in param["range_factors"]])
            case "binary":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.binary_decay(int(param["max_range"]))
            case "linear":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.linear_decay(int(param["max_range"]))
            case "exponential":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.exponential_decay(int(param["max_range"]))
            case "gaussian":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.gaussian_decay(int(param["max_range"]))
            case "inverse-power":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.inverse_power_decay(int(param["max_range"]))
            case "kernel-density":
                if "max_range" not in param:
                    return None
                if param["max_range"] <= 0:
                    return None
                return pyaccess.kernel_density_decay(int(param["max_range"]), 0.75)
            case "polynom":
                if "max_range" not in param or "range_factors" not in param:
                    return None
                if param["max_range"] <= 0 or len(param["range_factors"]) == 0:
                    return None
                return pyaccess.polynomial_decay(int(param["max_range"]), [float(i) for i in param["range_factors"]])
            case "piecewise-linear":
                if "ranges" not in param or "range_factors" not in param:
                    return None
                if len(param["ranges"]) == 0 or len(param["range_factors"]) != len(param["ranges"]):
                    return None
                return pyaccess.piecewise_linear_decay([int(i) for i in param["ranges"]], [float(i) for i in param["range_factors"]])
            case _:
                return None
    except:
        return None
