"""
command data structure:
{
    "name": "..."
    ["description": "...",]
    ["params": {
        "param1": {
            "description": "...",
            "required": True
            "default": "..."
        }
    }]
}
"""
def usage_string(name, params):
    parts = [f"Usage: /{name} [flags=<flags>]"]
    for param in params:
        if params[param]["required"]:
            parts.append(f"{param}=<{param}>")
        else:
            parts.append(f"[{param}=<{param}>]")
    return ";".join(parts)


def help_string(data: dict):
    name = data["name"]
    description = data.get("description", "No description provided")
    params = data.get("params", {})
    lines = [description]
    usage = usage_string(name, params)
    lines.append(usage)
    lines.append("\nParameters:")
    for param in params:
        lines.append(f"    {param}: {params[param]['description']}")
    return f'```{"\n".join(lines)}```'