using UnityEditor;
using UnityEngine;


public static class GameData
{
    public static int game_id;
    public static Card[] player_cards = new Card[2];
    public static Card[] drawn_cards = new Card[5];
    public static int money_pool;
    public static int player_total;
    public static int player_put;
    public static int opponent_total;
    public static int opponent_put;
    public static string state;
}
