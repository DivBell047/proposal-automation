import streamlit as st

def format_enum_options(enum_cls):
    """Returns list of values for streamlit selectboxes"""
    return [e.value for e in enum_cls]

def dropdown_with_other(label, options, key_prefix):
    """
    Renders a selectbox with an 'other' option.
    Returns the selected value or the custom input.
    """
    options_with_other = options + ["other"]
    selected = st.selectbox(label, options_with_other, key=f"{key_prefix}_select")
    
    if selected == "other":
        custom_val = st.text_input(f"Specify {label}", key=f"{key_prefix}_custom")
        return custom_val if custom_val else "other"
    return selected
