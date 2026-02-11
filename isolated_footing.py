import math


def get_strength_value(input):
    strength_val = int(input.split('-')[1])  # Fe-415, M-20
    return strength_val


def upward_soil_pressure(w, x, y, q_u):
    # Upward Soil Pressure (Pu) = Total load / Area of footing
    p_u = w / (x * y)

    # factored soil pressure(Puf) = soil pressure * F.O.S
    p_u_f = p_u * 1.5

    # -------------------------------CHECK FOR SBC-------------------------
    print(f"Upward Soil Pressure(Pu) = {p_u:.2f} kN/m²")
    print(f"Factored Soil Pressure(Puf) = {p_u_f:.2f} kN/m²")

    if p_u <= q_u:
        print("_SUCCESS It's Safe to use this Upward pressure")
    else:
        print("_DANGER The upward soil pressure exceeds the safe bearing capacity!")

    return p_u, p_u_f


def checking_one_way_shear_criterion(a, b, x, y, p_u_f, d):
    # for one-way shear criterion the critical section for shear is at a distance of d from the face of the footing
    # IS 456:2000, Clause 34.2.4.1

    # One-way shear forces
    V_u_x = p_u_f * y * ((x / 2) - (a / 2) - d)
    V_u_y = p_u_f * x * ((y / 2) - (b / 2) - d)

    V_u = max(V_u_x, V_u_y)

    # Shear stress in kN/m²
    if V_u_x >= V_u_y:
        tau_v = V_u_x / (y * d)
    else:
        tau_v = V_u_y / (x * d)

    # Concrete shear strength (assumed tau_c =0.36 N/mm², fot 0.25% of reinforcement from Table 19)
    tau_c = 0.36 * 1000  # KN/m²

    # Check
    if tau_v <= tau_c:
        print("_SUCCESS One-way shear SAFE")
    else:
        print("_DANGER One-way shear NOT SAFE")

    return tau_v, tau_c


def checking_two_way_shear_criterion(a, b, x, y, p_u_f, fck, d):
    # for two-way shear criterion the critical section for shear is at a distance of d / 2 from the face of the footing
    # IS 456:2000, Clause 31.6.1

    # Perimeter of critical section(b0) = 2 * {(column width + effective depth) + (column length + effective depth)}
    b_0 = 2 * ((a + d) + (b + d))

    # Punching Shear Force (Vu) = Factored soil pressure * (Area of footing - Area inside)
    v_u = p_u_f * ((x * y) - ((a + d) * (b + d)))

    # Punching Shear Stress (tau_v) = Punching SF / (perimeter of critical section * effective depth)
    tau_v = v_u / (b_0 * d)

    # Shear stress resisted or allowable shear stress as per IS 456:2000 Clause IS 456:2000, Clause 31.6.3.1
    tau_c = 0.25 * math.sqrt(fck)
    tau_c = tau_c * 1000  # converting to kN/m²

    # Check
    if tau_v <= tau_c:
        print("_SUCCESS Two-way shear SAFE")
    else:
        print("_DANGER Two-way shear NOT SAFE")

    return tau_v, tau_c


def checking_moment_criterion(m_u, x, f_ck, d):
    # for moment criterion critical section is at face of the column as per IS456:2000, Clause 34.2.3.2
    m_r = m_r = 0.138 * f_ck * (x * 1000) * (d * 1000) ** 2 / 1e6  # assuming Xumax / d = 0.48

    # Check
    if m_u <= m_r:
        print("_SUCCESS Moment is SAFE")
    else:
        print("_DANGER Moment is NOT SAFE")

    return m_r


def calculation_of_reinforcement(m_u, f_y, x, y, d):
    # as per IS456:2000, Annex G.1.1
    # Mu = 0.87 * fy * Ast * j * d, where Ast = area of reinforcement, j = lever arm depth factor = 0.9 (approximately)
    a_st_gross = m_u / (0.87 * f_y * 0.9 * d * 1000)  # converting fy into KN/m²

    # minimum reinforcement = 0.12 % of the gross area
    a_st_min = (0.12 / 100) * x * y

    # Check
    if a_st_gross < a_st_min:
        print("_DANGER Reinforcement calculated is less than minimum reinforcement criterion")
    elif a_st_gross >= a_st_min:
        print("_SUCCESS Reinforcement calculation is SAFE")

    # let us assume 16 mm dia bar both in long and short direction
    dia = 16 / 1000
    a_st_single = math.pi / 4 * dia ** 2

    # Spacing
    s = math.floor((a_st_single / a_st_gross) * (x * 1000))  # in both direction

    print("16 mm dia reinforcement is provided")
    print(f"Reinforcement requirement is {a_st_gross * 1000 ** 2: .2f} mm²")
    print(f"Spacing provided is {s} mm")

    return a_st_gross, s, dia


def development_length(f_ck, f_y):
    # Development length (L_d) = (0.87 * fy * dia) / 4 * tau_bd, where tau_bd = Bond stress, which is approximate 47 * dia for Fe 415 and 57 * dia for Fe 500
    # IS 456:2000 Clause 26.2.1
    dia = 16 / 1000

    if f_y == 415:
        l_d = 47 * dia
    elif f_y == 500:
        l_d = 57 * dia

    print(f"Development Length for {f_y} is {l_d} m")

    return l_d


def check_development_length(x, a, l_d):
    l_available = (x - a) / 2  # m

    if l_available >= l_d:
        return True
    else:
        return False


def main_function(input_dict):
    f_ck = get_strength_value(input_dict.get('conc_grd'))
    f_y = get_strength_value(input_dict.get('reinf_grd'))
    a = input_dict.get('colm_wid')
    b = input_dict.get('colm_len')
    h = input_dict.get('colm_ht')
    x = input_dict.get('footing_wid')
    y = input_dict.get('footing_len')
    d = input_dict.get('footing_depth')
    q_u = input_dict.get('safe_bearing_capacity')
    m_u = input_dict.get('moment')
    w_c = input_dict.get('axial_load')

    # In structural design, a common thumb rule is to assume the self-weight of the footing (plus backfill soil) is 10% of the axial column load.
    # Weight of the footing (Wc) = 10% of Axial load (Wc)
    # Total load (W) = Weight of column (Wc) + Weight of footing (Wf)
    w_f = 0.1 * w_c
    w = w_c + w_f

    print(f"Weight of Footing is: {w_f:.2f} KN\nTotal weight (Footing and Column): {w} KN")

    # upward soil pressure check
    p_u, p_u_f = upward_soil_pressure(w, x, y, q_u)

    # one way shear check
    tau_one = checking_one_way_shear_criterion(a, b, x, y, p_u_f, d)

    # punching shear check
    tau_two = checking_two_way_shear_criterion(a, b, x, y, p_u_f, f_ck, d)

    # moment check
    mor = checking_moment_criterion(m_u, x, f_ck, d)

    # reinfocement calculation
    a_reinf = calculation_of_reinforcement(m_u, f_y, x, y, d)

    # development check
    l_dev = development_length(f_ck, f_y)

    if check_development_length(x, a, l_dev):
        print("_SUCCESS Development length OK")
    else:
        print("_DANGER Development length NOT OK – revise footing or provide hooks")

    return p_u, p_u_f, tau_one, tau_two, mor, a_reinf, l_dev

# -------------CALLING THE MAIN FUNCTION------------------------------------
main_function(input_dict)