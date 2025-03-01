

"""
    SN29500 - 2
"""
# For analog integrated circuits with an extended range of operating voltage
def calculate_fr_integrated_circuit_extended_voltage(Pi_Ref, Pi_U, Pi_T, Pi_D):
    return Pi_Ref * Pi_U * Pi_T * Pi_D

# For analog integrated circuits with fixed operating voltage
def calculate_fr_integrated_circuit_fixed_voltage(Pi_Ref, Pi_T, Pi_D):
    return Pi_Ref * Pi_T * Pi_D

# For Digital CMOS B families
def calculate_fr_digital_cmos_b(Pi_Ref, Pi_U, Pi_T):
    return Pi_Ref * Pi_U * Pi_T

# For all other Integrated Circuits
def calculate_fr_integrated_circuit(Pi_Ref, Pi_T):
    return Pi_Ref * Pi_T


"""
    SN29500 - 3
"""
# For Bipolar transistor, universal transistor  and transistor arrays
def calculate_fr_bipolar_transistor(Pi_Ref, Pi_U, Pi_T, Pi_D):
    return Pi_Ref * Pi_U * Pi_T * Pi_D

# For other transistors
def calculate_fr_transistor(Pi_Ref, Pi_U, Pi_T):
    return Pi_Ref * Pi_U * Pi_T

# For universal and schottky diodes
def calculate_fr_schottky_diode(Pi_Ref, Pi_D, Pi_T):
    return Pi_Ref * Pi_D * Pi_T

# For other diodes and power semiconductors
def calculate_fr_diode(Pi_Ref, Pi_T):
    return Pi_Ref * Pi_T


"""
    SN29500 - 4
"""

# For Capacitors
def calculate_fr_capacitor(Pi_Ref, Pi_U, Pi_T, Pi_Q):
    return Pi_Ref * Pi_U * Pi_T * Pi_Q

# For resistors and inductors
def calculate_fr_resistor_inductor(Pi_Ref, Pi_T):
    return Pi_Ref * Pi_T

# For other passive components
def calculate_fr_passive(Pi_Ref):
    return Pi_Ref


"""
    SN29500 - 7
"""

# For relays
def calculate_fr_relay(Pi_Ref, Pi_L, Pi_E, Pi_T, Pi_K):
    return Pi_Ref * Pi_L * Pi_E * Pi_T * Pi_K

"""
    SN29500 - 9
"""

# For switches and buttons
def calculate_fr_switch_button(Pi_Ref, Pi_L, Pi_E):
    return Pi_Ref * Pi_L * Pi_E

"""
    SN29500 - 10
"""

# For signals and pilot lamps
def calculate_fr_signal_pilot_lamp(Pi_Ref, Pi_U):
    return Pi_Ref * Pi_U

"""
    SN29500 - 11
"""

# For contactors
def calculate_fr_contactor(Pi_Ref, Pi_S, Pi_U, Pi_I, Pi_T, Pi_E):
    return Pi_Ref * Pi_S * Pi_U * Pi_I * Pi_T * Pi_E

"""
    SN29500 - 15
"""

# For electromagnetic protection devices
def calculate_fr_electromagnetic_protection_device(Pi_Ref, Pi_U, Pi_I, Pi_T, Pi_S, Pi_E):
    return Pi_Ref * Pi_U * Pi_I * Pi_T * Pi_S * Pi_E

"""
    SN29500 - 16
"""

# For electromechanical pushbutton, Signaling device and position switches in low voltage network
def calculate_fr_electromechanical_pushbutton_signaling_device_position_switches(Pi_Ref, Pi_S, Pi_I, Pi_E, Pi_T, Pi_U):
    return Pi_Ref * Pi_S * Pi_I * Pi_E * Pi_T * Pi_U


"""
    SN29500 - 5
"""

# Considering only solder now
def calculate_fr_solder():
    return 0.03

"""
    SN29500 - 6
"""
# Considering only socket
# plug in contacts that must be inserted without electrical load
def calculate_fr_socket():
    return 3 # Single contacts