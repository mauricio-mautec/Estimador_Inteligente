class ModeloTreinadoQueries:
    INSERT = """
        INSERT INTO modelo_treinado
            (modelo_treinado_id, modelo_id, usuario_id, payload, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    SELECT_BY_ID = """
        SELECT *
        FROM modelo_treinado
        WHERE modelo_treinado_id = %s
    """
    SELECT_BY_USUARIO = """
        SELECT *
        FROM modelo_treinado
        WHERE usuario_id = %s
        ORDER BY criado_em DESC
    """
    UPDATE_STATUS = """
        UPDATE modelo_treinado
        SET status       = %s,
            iniciado_em  = %s,
            concluido_em = %s,
            resultado    = %s,
            erro         = %s
        WHERE modelo_treinado_id = %s
    """
