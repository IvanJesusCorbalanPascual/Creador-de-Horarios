CREATE TABLE public.ciclos (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre text NOT NULL UNIQUE,
  CONSTRAINT ciclos_pkey PRIMARY KEY (id)
);
CREATE TABLE public.competencia_profesor (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  profesor_id integer,
  modulo_id integer,
  CONSTRAINT competencia_profesor_pkey PRIMARY KEY (id),
  CONSTRAINT competencia_profesor_profesor_id_fkey FOREIGN KEY (profesor_id) REFERENCES public.profesores(id),
  CONSTRAINT competencia_profesor_modulo_id_fkey FOREIGN KEY (modulo_id) REFERENCES public.modulos(id)
);
CREATE TABLE public.horario_generado (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  profesor_id integer,
  modulo_id integer,
  dia_semana integer NOT NULL,
  hora_inicio time without time zone NOT NULL,
  hora_fin time without time zone NOT NULL,
  version_horario integer DEFAULT 1,
  CONSTRAINT horario_generado_pkey PRIMARY KEY (id),
  CONSTRAINT horario_generado_profesor_id_fkey FOREIGN KEY (profesor_id) REFERENCES public.profesores(id),
  CONSTRAINT horario_generado_modulo_id_fkey FOREIGN KEY (modulo_id) REFERENCES public.modulos(id)
);
CREATE TABLE public.modulos (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre text NOT NULL,
  ciclo_id integer,
  horas_semanales integer NOT NULL,
  horas_max_dia integer DEFAULT 3,
  profesor_asignado text,
  CONSTRAINT modulos_pkey PRIMARY KEY (id),
  CONSTRAINT modulos_ciclo_id_fkey FOREIGN KEY (ciclo_id) REFERENCES public.ciclos(id)
);
CREATE TABLE public.preferencias (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  profesor_id integer,
  dia_semana integer NOT NULL,
  hora_inicio time without time zone NOT NULL,
  hora_fin time without time zone NOT NULL,
  nivel_prioridad integer NOT NULL CHECK (nivel_prioridad = ANY (ARRAY[0, 1, 2])),
  motivo text,
  CONSTRAINT preferencias_pkey PRIMARY KEY (id),
  CONSTRAINT preferencias_profesor_id_fkey FOREIGN KEY (profesor_id) REFERENCES public.profesores(id)
);
CREATE TABLE public.profesor_ciclo (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  ciclo_id integer,
  profesor_id integer,
  CONSTRAINT profesor_ciclo_pkey PRIMARY KEY (id),
  CONSTRAINT profesor_ciclo_ciclo_id_fkey FOREIGN KEY (ciclo_id) REFERENCES public.ciclos(id),
  CONSTRAINT profesor_ciclo_profesor_id_fkey FOREIGN KEY (profesor_id) REFERENCES public.profesores(id)
);
CREATE TABLE public.profesores (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre text NOT NULL,
  color_hex text DEFAULT '#3388ff'::text,
  horas_max_dia integer DEFAULT 6,
  horas_max_semana integer DEFAULT 20,
  CONSTRAINT profesores_pkey PRIMARY KEY (id)
);