% Archivo generado a partir de reglas canonicas y catalogo demo.

carrera(ingenieria_de_sistemas).
carrera(ingenieria_de_software).
carrera(ciencia_de_datos).
carrera(ciberseguridad).
carrera(psicologia).
carrera(trabajo_social).
carrera(diseno_ux_ui).

pertenece_area(ingenieria_de_sistemas, tecnologia_ingenieria).
pertenece_area(ingenieria_de_software, tecnologia_ingenieria).
pertenece_area(ciencia_de_datos, datos).
pertenece_area(psicologia, psicologia).
pertenece_area(diseno_ux_ui, diseno).

requiere_habilidad(ingenieria_de_sistemas, pensamiento_logico).
requiere_habilidad(ciencia_de_datos, analisis_numerico).
requiere_habilidad(psicologia, empatia).
requiere_habilidad(diseno_ux_ui, pensamiento_visual).

recomendar(Estudiante, ingenieria_de_sistemas) :-
    interes(Estudiante, tecnologia),
    habilidad(Estudiante, pensamiento_logico).

recomendar(Estudiante, ciencia_de_datos) :-
    interes(Estudiante, datos),
    habilidad(Estudiante, analisis_numerico).

recomendar(Estudiante, psicologia) :-
    interes(Estudiante, social),
    habilidad(Estudiante, empatia).

recomendar(Estudiante, diseno_ux_ui) :-
    interes(Estudiante, diseno),
    habilidad(Estudiante, pensamiento_visual).

requiere_refuerzo(Estudiante, comunicacion) :-
    \+ habilidad(Estudiante, comunicacion).
