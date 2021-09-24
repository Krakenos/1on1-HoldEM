using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.SceneManagement;

public class StartGame : MonoBehaviour
{
    public GameObject selector;
    private void Start()
    {
        
    }
    public void OnButtonPress(){
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
        GameData.game_id = (int) parsedJsonResponse["id"];
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
