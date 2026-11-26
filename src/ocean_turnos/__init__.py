"""Agentes da equipe para o Ocean 1.1 no Modo por Turnos.

Fluxo de um turno:
    pacote (GET /api/v1/turn/pack)
      -> economia e navegação propõem
      -> segurança revisa (código)
      -> coordenador monta a decisão
    decisão (POST /api/v1/turn/submit) -> próximo pacote

Nada aqui altera o simulador. O servidor cuida de heartbeats, hashes e assinaturas.
"""

__version__ = "0.1.0"
