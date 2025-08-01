#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo principal do jogo, gerencia o loop de jogo e a progressão das fases.
Atualizado para incluir o sistema de inventário completo.
"""

import pygame
import sys
from src.config import *
from src.ui.menu import tela_inicio, tela_game_over, tela_vitoria_fase
from src.game.fase import jogar_fase
from src.utils.visual import criar_gradiente
from src.ui.loja import tela_loja
from src.game.inventario import tela_inventario  # CORRIGIDO: importação do local correto
from src.ui.selecao_fase import tela_selecao_fase
from src.utils.progress import ProgressManager
import os
import json

def main_game():
    """
    Função principal de controle do jogo.
    Gerencia o loop de jogo, menus, loja, inventário e progressão de fases.
    Ajustada para incluir o sistema completo de inventário.
    """
    
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    tela = pygame.display.set_mode((LARGURA, ALTURA))

    pygame.display.set_caption(TITULO)
    relogio = pygame.time.Clock()

    # Adicionar um ícone para a janela
    icon_surf = pygame.Surface((32, 32))
    icon_surf.fill(PRETO)
    pygame.draw.rect(icon_surf, AZUL, (5, 5, 22, 22))
    pygame.display.set_icon(icon_surf)

    # Carregar ou criar fontes
    try:
        fonte_titulo = pygame.font.Font(None, 60)  # None usa a fonte padrão
        fonte_normal = pygame.font.Font(None, 36)
        fonte_pequena = pygame.font.Font(None, 24)
    except:
        fonte_titulo = pygame.font.SysFont("Arial", 60, True)
        fonte_normal = pygame.font.SysFont("Arial", 36, True)
        fonte_pequena = pygame.font.SysFont("Arial", 24)

    # Criar gradientes para diferentes telas
    try:
        gradiente_jogo = criar_gradiente((0, 0, 30), (0, 0, 60))
        gradiente_menu = criar_gradiente((30, 0, 60), (10, 0, 30))
        gradiente_vitoria = criar_gradiente((0, 50, 0), (0, 20, 40))
        gradiente_derrota = criar_gradiente((50, 0, 0), (20, 0, 40))
        gradiente_loja = criar_gradiente(ROXO_CLARO, ROXO_ESCURO)
        gradiente_inventario = criar_gradiente((50, 20, 100), (20, 10, 60))  # Novo gradiente para inventário
        gradiente_selecao = criar_gradiente((20, 20, 50), (10, 10, 30))  # Gradiente para seleção de fase
    except Exception as e:
        return

    # Adicionar ProgressManager
    try:
        progress_manager = ProgressManager()
    except Exception as e:
        return
    
    # Carregar upgrades se existirem
    try:
        if os.path.exists("data/upgrades.json"):
            with open("data/upgrades.json", "r") as f:
                upgrades = json.load(f)
                # Get value but don't reset it in the save file yet
                shotgun_ammo = upgrades.get("espingarda", 0)
                machinegun_ammo = upgrades.get("metralhadora", 0)
    except Exception as e:
        print(f"⚠️ Aviso ao carregar upgrades: {e}")
    
    # Loop principal do jogo
    while True:
        try:
            # Mostrar tela de início
            opcao_menu = tela_inicio(tela, relogio, gradiente_menu, fonte_titulo)
            
            # Variável para armazenar fase selecionada
            fase_atual = None
            
            if opcao_menu == "loja":
                # O jogador escolheu ir para a loja
                tela_loja(tela, relogio, gradiente_loja)
                continue  # Volta para o menu principal
            elif opcao_menu == "inventario":
                # O jogador escolheu ir para o inventário
                tela_inventario(tela, relogio, gradiente_inventario, fonte_titulo, fonte_normal)
                continue  # Volta para o menu principal
            elif opcao_menu == "selecao_fase":
                # O jogador escolheu selecionar fase
                fase_selecionada = tela_selecao_fase(tela, relogio, gradiente_selecao, fonte_titulo, fonte_normal)
                if fase_selecionada is not None:
                    fase_atual = fase_selecionada
                    # Continuar para jogar a fase selecionada
                    opcao_menu = "jogar"
                else:
                    continue  # Volta para o menu principal
            
            if opcao_menu == False:  # Sair do jogo
                return
            
            # Se não foi para a loja, inventário nem saiu, então o jogador quer jogar
            
            # Variáveis de fase
            if fase_atual is None:  # Se não selecionou uma fase específica
                fase_atual = progress_manager.obter_fase_maxima()
            else:
                print(f" Fase selecionada pelo jogador: {fase_atual}")  # Debug
            
            # Loop de fases
            while fase_atual <= MAX_FASES:
                
                # Jogar a fase atual
                resultado = jogar_fase(tela, relogio, fase_atual, gradiente_jogo, fonte_titulo, fonte_normal)

                # Adicionar esta verificação para retorno ao menu
                if resultado == "menu":
                    # Voltar diretamente para o menu quando pausado
                    break  # Sai do loop de fases e volta para o menu principal
                
                if not resultado:
                    # Se o jogador perdeu
                    opcao = tela_game_over(tela, relogio, gradiente_vitoria, gradiente_derrota, False, fase_atual)
                    if opcao:  # True = jogar de novo
                        break  # Sai do loop de fases para reiniciar do menu
                    else:
                        return  # False = sair do jogo
                
                # Jogador completou a fase
                if fase_atual < MAX_FASES:
                    # Atualizar progresso
                    progress_manager.atualizar_progresso(fase_atual + 1)
                    
                    # Se não for a última fase, mostra tela de vitória intermediária
                    opcao = tela_vitoria_fase(tela, relogio, gradiente_vitoria, fase_atual)
                    
                    if opcao == "proximo":
                        # Avançar para próxima fase
                        fase_atual += 1
                    elif opcao == "menu":
                        # Voltar ao menu principal
                        break
                    else:  # "sair"
                        # Sair do jogo
                        return
                else:
                    # Atualizar progresso para indicar que completou todas as fases
                    progress_manager.atualizar_progresso(MAX_FASES)
                    
                    # Jogador completou a última fase
                    opcao = tela_game_over(tela, relogio, gradiente_vitoria, gradiente_derrota, True, MAX_FASES)
                    if not opcao:  # False = sair do jogo
                        return
                    break  # Sai do loop de fases para reiniciar do menu
                    
        except Exception as e:
            import traceback
            traceback.print_exc()
            return