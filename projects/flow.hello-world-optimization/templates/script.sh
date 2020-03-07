{% extends base_script %}
{% block body %}
# Resubmit operations
sleep 1; python project.py submit
{{ super() }}
{% endblock %}
{% block footer %}
{{ super() }}
# Resubmit operations
sleep 1; python project.py submit
{% endblock %}
