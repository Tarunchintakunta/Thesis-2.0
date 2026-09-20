package terraform.helpers

import rego.v1

is_world_cidr(x) if {
	is_string(x)
	x == "0.0.0.0/0"
}

is_world_cidr(x) if {
	is_string(x)
	x == "::/0"
}

is_star(x) if {
	is_string(x)
	x == "*"
}

is_var_ref(x) if {
	is_string(x)
	startswith(x, "var.")
}

is_var_ref(x) if {
	is_string(x)
	startswith(x, "${var.")
}

is_falsey(x) if x == false

is_falsey(x) if {
	is_string(x)
	x == "false"
}

is_falsey(x) if {
	is_string(x)
	x == ""
}

is_falsey(x) if x == null

is_empty_list(x) if {
	is_array(x)
	count(x) == 0
}

resource_types contains t if {
	some t
	input.resource[t]
}

has_resource(t) if t in resource_types
