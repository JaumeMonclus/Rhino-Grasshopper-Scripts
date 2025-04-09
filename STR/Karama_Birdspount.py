import math as mt

# esforços a compressión

ecc = 4.69
ecp = 2.87

# esforços a tracción

etc = 1.13
etp = 1.55

# Cortantes 

Vz = -0.66
Vy = -0.82

# Cortantes totales (me faltan los cortantes puntuales i constantes)

Vt = (Vz**2 + Vy**2)**0.5

Nid = 1.35*ecp + 1.5*ecc
Vid = 1.5*1.35*Vt

# En el tirante C22
#  a = a la bisectriz de b por la interseccion del tirante con el par


b = 30
a = b/2

a = mt.radians(a)
b = mt.radians(b)

# descomposicion de fuerzas 

F1 = Nid*mt.cos(a) - Vid*mt.sin(a)
F2 = Nid*mt.sin(a) + Vid*mt.cos(a)
F3 = Nid*mt.cos(b) - Vid*mt.sin(b)
F4 = F1*mt.sin(a) + F2*mt.cos(a)

# Compresion oblicua en el frente de la barbilla


o_cad_sub = 60*80/mt.cos(a)
o_cad = F1*10**3/o_cad_sub

# Resistencia a compresion oblicua ( valores de promptuario)

f_c0d = 13.85
f_c90d = 1.66

# K_c90 = es un coeficiente no aplicable en estos casos
# Resistencia a compresión oblicua (fórmula corregida para grados)

f_c_alpha_d = ((f_c0d * (mt.sin(a)**2)/ f_c90d) + mt.cos(a)**2)

f_c_alpha_d = f_c0d / f_c_alpha_d

# Indice d agotamiento  en compresión oblcua

i_agotamiento_oblicua = o_cad / f_c_alpha_d

print("El indice de agotamiento en compresion oblicua es: ", i_agotamiento_oblicua)



