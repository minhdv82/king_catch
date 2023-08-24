import argparse

from src.game_view import KingGameView

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--network', type=int, choices=[0, 1, 2],
                        default=0, help='For playing via network. 0: offline; 1: server; 2: client')
    parser.add_argument('--mode', type=int, choices=[0, 1, 2],
                        default=0, help='Game mode: 0 = man_vs_man; 1 = man_vs_ai; 2 = ai_vs_ai')
    parser.add_argument('--type', type=int, choices=[0, 1],
                        default=0, help='Game type. 0 = invisible; 1 = visible')
    
    args = parser.parse_args()

    kg = KingGameView(game_mode=args.mode, game_type=args.type, network=args.network)
    kg.game_loop()    


if __name__=='__main__':
    main()
