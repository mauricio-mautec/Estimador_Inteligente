class ModeloQueries:
    SELECT_ALL = """
        SELECT modelo_id, tipo, payload_schema, criado_em, atualizado_em
        FROM modelo
        ORDER BY tipo
    """
    SELECT_BY_ID = """
        SELECT modelo_id, tipo, payload_schema, criado_em, atualizado_em
        FROM modelo
        WHERE modelo_id = %s
    """
    SELECT_BY_TIPO = """
        SELECT modelo_id, tipo, payload_schema, criado_em, atualizado_em
        FROM modelo
        WHERE tipo = %s
    """
