import numpy as np
import streamlit as st
import plotly.graph_objects as go

import st_utils as _st

st.set_page_config(
    page_title="Maximum Shearing Stress",
    page_icon="https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/58/000000/external-mountains-camping-vitaliy-gorbachev-flat-vitaly-gorbachev.png",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": """   
         Developed with ❤ by [Francesco Franco](https://www.linkedin.com/in/francesco-franco-alva-73b6321b8/)\n
         Inspired in [Nord Theme](https://www.nordtheme.com/)
         """
    },
)

st.markdown(_st.CUSTOM_FONT_URL, unsafe_allow_html=True)

colours = _st.DEFAULT_THEME
colours = [*colours.values()][1:]

###########
# Sidebar #
###########

with st.sidebar:
    _st.googlef_text("⛰️ Maximum Shearing Stress", key="h1")

    _st.googlef_text("Settings ⚙️", key="h2")

    unit = st.selectbox("Stress Units 📐", ("kPa", "kg/cm²"))

    if unit == "kPa":
        unit2 = "kN"
    else:
        unit2 = "kg"

##############
# Encabezado #
##############

_st.set_header("Geotechnical Memories 🌙", key="h1")

_st.googlef_text("⛰️ Maximum Shearing Stress", key="h2")

############################################
# Primer bloque: Parámetros de Resistencia #
############################################

_st.googlef_text("1️⃣ Shear Strength Parameters", key="h3")

if "params" not in st.session_state:
    st.session_state["params"] = [None] * 3

with st.form("input_parameters"):

    col11, col12, col13 = st.columns([1.0, 0.8, 1.0])

    with col11:
        c = st.number_input(
            "Cohesive parameter ({})".format(unit),
            step=5.00 if unit == "kPa" else 0.05,
            min_value=0.00,
            max_value=25.00 if unit == "kPa" else 0.25,
            value=0.00,
        )

    with col12:
        phi = st.number_input(
            "Friction angle (°)",
            step=5.0,
            min_value=0.0,
            max_value=15.0,
            value=0.0,
        )

    with col13:
        Ko = st.number_input(
            "Earth pressure coefficient",
            value=1 - np.sin(np.deg2rad(phi)),
            disabled=True,
        )

    col1, col2, col3 = st.columns(3)

    with col2:
        input_verf = st.form_submit_button(label="🚀 Load Parameters!")


if not input_verf:
    pass
elif input_verf and Ko != 1:
    st.session_state.params[0] = c
    st.session_state.params[1] = phi
    st.session_state.params[2] = Ko
else:
    st.error("❌ Friction angle must be greater than zero.")

##########################################################
# Segundo bloque: Variación del Esfuerzo Cortante Máximo #
##########################################################

_st.googlef_text("2️⃣ Shear Strength Variation", key="h3")

c = st.session_state.params[0] if unit == "kPa" else min(st.session_state.params[0], 0.25)
phi = st.session_state.params[1]
Ko = st.session_state.params[2]


if all(st.session_state.params[1:]):
    maxv_stress = 500.0 if unit == "kPa" else 5.0

    col21, col22 = st.columns([1.8, 1.0])

    with col21:
        v_stress = st.slider(
            "Vertical stress ({})".format(unit),
            min_value=0.0,
            max_value=maxv_stress,
            step=20.0 if unit == "kPa" else 0.1,
        )

    with col22:
        m_stress = st.number_input(
            "Mean stress ({})".format(unit),
            value=(Ko + 1) * v_stress / 2,
            disabled=True,
        )

    radius = v_stress * (1 - Ko) / 2

    maximum_shear = np.sqrt(
        (m_stress * np.sin(np.deg2rad(phi)) + c * np.cos(np.deg2rad(phi))) ** 2
        - radius**2
    )

    col31, col32 = st.columns([1.8, 1.0])

    with col32:
        show_max_circle = st.radio(
            "Show failure state?",
            ["Yes", "No"],
            index=1,
            disabled=True if not v_stress else False,
        )

    with col31:
        maximum_shear = st.number_input(
            "Maximum shearing stress ({})".format(unit),
            value=0 if not show_max_circle else maximum_shear,
            disabled=True,
        )

    rango_p1 = [0, 550 if unit == "kPa" else 5.5]

    rango_q1 = [np.tan(np.deg2rad(phi)) * p + c for p in rango_p1]
    rango_q2 = [-np.tan(np.deg2rad(phi)) * p - c for p in rango_p1]

    fig = go.Figure()

    # Mohr Coulomb Circle
    fig.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=Ko * v_stress,
        y0=-radius,
        x1=v_stress,
        y1=radius,
        opacity=1.0,
        line=dict(color=colours[0], width=2),
        fillcolor="rgba(0,0,0,0)",
    )

    # Mohr Coulomb Envelope Positive
    fig.add_trace(
        go.Scatter(
            x=rango_p1,
            y=rango_q1,
            mode="lines",
            line={"color": colours[2], "width": 2},
        )
    )

    # Mohr Coulomb Envelope Negative
    fig.add_trace(
        go.Scatter(
            x=rango_p1,
            y=rango_q2,
            mode="lines",
            line={"color": colours[2], "width": 2},
            name="Envelope",
        )
    )

    # Mohr Coulomb Envelope Note
    if v_stress == 0:
        fig.add_annotation(
            x=2 * rango_p1[1] / 5,
            y=2 * rango_q1[1] / 5,
            text=" c = {:.2f} ‖ Φ = {:.2f}° ".format(c, phi),
            showarrow=False,
            bordercolor=colours[2],
            borderwidth=1.5,
            borderpad=7,
            bgcolor=colours[3],
            font={"color": colours[1], "size": 12.5},
        )

    # Maximum Shear Circle
    max_circle_radius = np.sqrt((v_stress - m_stress) ** 2 + maximum_shear**2)
    if show_max_circle == "Yes":
        fig.add_shape(
            type="circle",
            xref="x",
            yref="y",
            x0=m_stress - max_circle_radius,
            y0=-max_circle_radius,
            x1=m_stress + max_circle_radius,
            y1=max_circle_radius,
            opacity=1.0,
            line=dict(color=colours[5], width=2, dash="dash"),
            fillcolor="rgba(0,0,0,0)",
        )

    fig.update_xaxes(
        fixedrange=True,
        range=[-50 if unit == "kPa" else -0.5, 550 if unit == "kPa" else 5.5],
        title_text="σ' ({0})".format(unit),
        tickfont_size=13,
        showgrid=True,
        gridwidth=1,
        gridcolor=colours[4],
        zerolinecolor=colours[2],
        zerolinewidth=2,
        showline=True,
        linecolor=colours[2],
        linewidth=2,
        tick0="xd",
    )

    fig.update_yaxes(
        title_text="τ ({0})".format(unit),
        tickfont_size=13,
        showgrid=True,
        gridwidth=1,
        gridcolor=colours[4],
        scaleanchor="x",
        scaleratio=1,
        zeroline=False,
        mirror=True,
        showline=True,
        linecolor=colours[2],
        linewidth=2,
    )

    fig.update_layout(
        dragmode="pan",
        font=dict(family=_st.CUSTOM_FONT, color=colours[3]),
        showlegend=False,
        template="seaborn",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=colours[3],
        margin=dict(l=0, r=0, b=0, t=0),
        hovermode=False,
    )

    st.plotly_chart(fig, config={"displayModeBar": False})

    _st.googlef_text("💡 Solution", key="h3")

    st.latex(
        r"""\tau_{\max }=\left\{\left[\frac{\left(1+K_{0}\right)}{2} \bar{\sigma}_{v} \sin \bar{\phi}+\bar{c} \cos \bar{\phi}\right]^{2}-\left[\frac{\left(1-K_{0}\right)}{2} \bar{\sigma}_{v}\right]^{2}\right\}^{1 / 2}"""
    )

else:
    "⌛ Waiting parameters..."
