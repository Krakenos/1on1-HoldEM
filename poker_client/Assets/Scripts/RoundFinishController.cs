using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class RoundFinishController : MonoBehaviour
{
    public Text winningText;
    public Text oppMoney;
    public Text playerMoney;
    void Start()
    {
        playerMoney.text = string.Format("Pieniądze: {0}", GameData.player_total);
        oppMoney.text = string.Format("Pieniądze: {0}", GameData.opponent_total);
        if (GameData.state == "lost")
        {
            winningText.text = "Przegrałeś";
        }
        else if (GameData.state == "won")
        {
            winningText.text = "Wygrałeś";
        }
    }

    void Update()
    {
        
    }
    public void NewGameClick()
    {
        Array.Clear(GameData.drawn_cards, 0, 5);
        Array.Clear(GameData.player_cards, 0, 2);
        GameData.drawn_cards = new Card[5];
        GameData.player_cards = new Card[2];
        var request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/start_game/");
        request.Method = "POST";
        request.ContentType = "application/json";
        string data = JsonConvert.SerializeObject(new { player_num = 2 });
        using (var streamWriter = new StreamWriter(request.GetRequestStream()))
        {
            streamWriter.Write(data);
            streamWriter.Flush();
            streamWriter.Close();
        }
        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        Debug.Log(jsonResponse);
        var parsedJsonResponse = JObject.Parse(jsonResponse);
        Debug.Log(parsedJsonResponse["id"]);
        GameData.game_id = (int)parsedJsonResponse["id"];
        request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id);
        request.Method = "GET";
        response = (HttpWebResponse)request.GetResponse();
        reader = new StreamReader(response.GetResponseStream());
        jsonResponse = reader.ReadToEnd();
        Debug.Log(jsonResponse);
        parsedJsonResponse = JObject.Parse(jsonResponse);
        for (int i = 0; i < 2; i++)
        {
            Card new_card = new Card();
            new_card.suit = (string)parsedJsonResponse["hand"][i]["suit"];
            new_card.value = (int)parsedJsonResponse["hand"][i]["value"];
            if (new_card.value == 14)
            {
                new_card.value = 1;
            }
            GameData.player_cards[i] = new_card;
        }
        GameData.money_pool = (int)parsedJsonResponse["money_pool"];
        GameData.player_put = (int)parsedJsonResponse["money_bet"];
        GameData.player_total = (int)parsedJsonResponse["money_total"];
        GameData.opponent_put = (int)parsedJsonResponse["opponent_bet"];
        GameData.opponent_total = (int)parsedJsonResponse["opponent_total"];
        GameData.state = "ongoing";
        SceneManager.LoadScene("Game", LoadSceneMode.Single);
    }
    public void ContinueClick()
    {
        Array.Clear(GameData.drawn_cards, 0, 5);
        Array.Clear(GameData.player_cards, 0, 2);
        GameData.drawn_cards = new Card[5];
        GameData.player_cards = new Card[2];
        var request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id + "/continue_game/");
        request.Method = "POST";
        request.ContentType = "application/json";
        string data = JsonConvert.SerializeObject(new { player_num = 2 });
        using (var streamWriter = new StreamWriter(request.GetRequestStream()))
        {
            streamWriter.Write(data);
            streamWriter.Flush();
            streamWriter.Close();
        }
        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        Debug.Log(jsonResponse);
        var parsedJsonResponse = JObject.Parse(jsonResponse);
        Debug.Log(parsedJsonResponse["id"]);
        GameData.game_id = (int)parsedJsonResponse["id"];
        request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id);
        request.Method = "GET";
        response = (HttpWebResponse)request.GetResponse();
        reader = new StreamReader(response.GetResponseStream());
        jsonResponse = reader.ReadToEnd();
        Debug.Log(jsonResponse);
        parsedJsonResponse = JObject.Parse(jsonResponse);
        for (int i = 0; i < 2; i++)
        {
            Card new_card = new Card();
            new_card.suit = (string)parsedJsonResponse["hand"][i]["suit"];
            new_card.value = (int)parsedJsonResponse["hand"][i]["value"];
            if (new_card.value == 14)
            {
                new_card.value = 1;
            }
            GameData.player_cards[i] = new_card;
        }
        GameData.money_pool = (int)parsedJsonResponse["money_pool"];
        GameData.player_put = (int)parsedJsonResponse["money_bet"];
        GameData.player_total = (int)parsedJsonResponse["money_total"];
        GameData.opponent_put = (int)parsedJsonResponse["opponent_bet"];
        GameData.opponent_total = (int)parsedJsonResponse["opponent_total"];
        GameData.state = "ongoing";
        SceneManager.LoadScene("Game", LoadSceneMode.Single);
    }
}
