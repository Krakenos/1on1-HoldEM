using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    public GameObject[] cardsArray;
    public GameObject PlayerArea;
    public GameObject OpponentArea;
    public GameObject Canvas;
    public GameObject playerCard;
    public GameObject playerCard2;
    public GameObject drawnCard;
    public Text moneyPool;
    public Text playerTotal;
    public Text playerPut;
    public Text opponentTotal;
    public Text opponentPut;

// Start is called before the first frame update
void Start()
    {
        Debug.Log(GameData.game_id);
        playerCard = Instantiate(cardsArray[0], new Vector3(-50, 0, 0), Quaternion.identity);
        playerCard.transform.SetParent(OpponentArea.transform, false);
        playerCard2 = Instantiate(cardsArray[0], new Vector3(50, 0, 0), Quaternion.identity);
        playerCard2.transform.SetParent(OpponentArea.transform, false);

        int suitmulti = suitToNumber(GameData.player_cards[0]);
        int suitmulti2 = suitToNumber(GameData.player_cards[1]);
        Debug.Log(suitmulti * 13 + GameData.player_cards[0].value);
        GameObject playerCard3 = Instantiate(cardsArray[suitmulti*13 + GameData.player_cards[0].value], new Vector3(-50, 0, 0), Quaternion.identity);
        playerCard3.transform.SetParent(PlayerArea.transform, false);
        GameObject playerCard4 = Instantiate(cardsArray[suitmulti2 * 13 + GameData.player_cards[1].value], new Vector3(50, 0, 0), Quaternion.identity);
        playerCard4.transform.SetParent(PlayerArea.transform, false);
        moneyPool.text = string.Format("Pula Pieniędzy: {0}", GameData.money_pool);
        playerTotal.text = string.Format("Pieniądze: {0}", GameData.player_total);
        playerPut.text = string.Format("Kwota Zakładu: {0}", GameData.player_put);
        opponentPut.text = string.Format("Kwota Zakładu: {0}", GameData.opponent_put);
        opponentTotal.text = string.Format("Pieniądze: {0}", GameData.opponent_total);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void CheckClick()
    {
        updateGame(1);
    }
    public void BetClick()
    {
        updateGame(2);
    }
    public void FoldClick()
    {
        updateGame(0);
    }
    public void updateGame(int choice)
    {
        var request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id + "/advance_game/");
        request.Method = "POST";
        request.ContentType = "application/json";
        string data = JsonConvert.SerializeObject(new { check = choice });
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
        string gameState = (string)parsedJsonResponse["result"];
        GameData.state = gameState;
        if (gameState == "ongoing")
        {
            request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id);
            request.Method = "GET";
            response = (HttpWebResponse)request.GetResponse();
            reader = new StreamReader(response.GetResponseStream());
            jsonResponse = reader.ReadToEnd();
            Debug.Log(jsonResponse);
            parsedJsonResponse = JObject.Parse(jsonResponse);
            var dealt_cards = parsedJsonResponse["dealt_cards"]["cards"];
            int counter = 0;
            GameData.money_pool = (int)parsedJsonResponse["money_pool"];
            GameData.player_put = (int)parsedJsonResponse["money_bet"];
            GameData.player_total = (int)parsedJsonResponse["money_total"];
            GameData.opponent_put = (int)parsedJsonResponse["opponent_bet"];
            GameData.opponent_total = (int)parsedJsonResponse["opponent_total"];
            updatePrices();
            deleteCards();
            foreach (var element in dealt_cards)
            {
                Debug.Log(element);
                Card new_card = new Card();
                new_card.suit = (string)element["suit"];
                new_card.value = (int)element["value"];
                if (new_card.value == 14)
                {
                    new_card.value = 1;
                }
                GameData.drawn_cards[counter] = new_card;
                counter++;
            }
            counter = 0;
            Debug.Log(GameData.drawn_cards);
            foreach (var card in GameData.drawn_cards)
            {
                if (card != null)
                {
                    Debug.Log(card);
                    int suit_mult = suitToNumber(card);
                    drawnCard = Instantiate(cardsArray[suit_mult * 13 + card.value], new Vector3(-200 + 100 * counter, 0, 0), Quaternion.identity);
                    drawnCard.transform.SetParent(Canvas.transform, false);
                    card.instance = drawnCard;
                    counter++;
                }
            }
        }
        if (gameState == "won")
        {

            request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id);
            request.Method = "GET";
            response = (HttpWebResponse)request.GetResponse();
            reader = new StreamReader(response.GetResponseStream());
            jsonResponse = reader.ReadToEnd();
            Debug.Log(jsonResponse);
            parsedJsonResponse = JObject.Parse(jsonResponse);
            GameData.money_pool = (int)parsedJsonResponse["money_pool"];
            GameData.player_put = (int)parsedJsonResponse["money_bet"];
            GameData.player_total = (int)parsedJsonResponse["money_total"];
            GameData.opponent_put = (int)parsedJsonResponse["opponent_bet"];
            GameData.opponent_total = (int)parsedJsonResponse["opponent_total"];
            updatePrices();
            Destroy(playerCard);
            Destroy(playerCard2);
            for (int i = 0; i < 2; i++)
            {
                Card new_card = new Card();
                new_card.suit = (string)parsedJsonResponse["cpu_hand"][i]["suit"];
                new_card.value = (int)parsedJsonResponse["cpu_hand"][i]["value"];
                if (new_card.value == 14)
                {
                    new_card.value = 1;
                }
                int multiplier = suitToNumber(new_card);
                playerCard = Instantiate(cardsArray[multiplier * 13 + new_card.value], new Vector3(-50 + i * 100, 0, 0), Quaternion.identity);
                playerCard.transform.SetParent(OpponentArea.transform, false);
            }
            SceneManager.LoadScene("RoundFinish", LoadSceneMode.Additive);
        }
        if (gameState == "lost")
        {
            request = (HttpWebRequest)WebRequest.Create(ServerConfig.API_URL + "game/" + GameData.game_id);
            request.Method = "GET";
            response = (HttpWebResponse)request.GetResponse();
            reader = new StreamReader(response.GetResponseStream());
            jsonResponse = reader.ReadToEnd();
            parsedJsonResponse = JObject.Parse(jsonResponse);
            GameData.money_pool = (int)parsedJsonResponse["money_pool"];
            GameData.player_put = (int)parsedJsonResponse["money_bet"];
            GameData.player_total = (int)parsedJsonResponse["money_total"];
            GameData.opponent_put = (int)parsedJsonResponse["opponent_bet"];
            GameData.opponent_total = (int)parsedJsonResponse["opponent_total"];
            updatePrices();
            Destroy(playerCard);
            Destroy(playerCard2);
            for (int i = 0; i < 2; i++)
            {
                Card new_card = new Card();
                new_card.suit = (string)parsedJsonResponse["cpu_hand"][i]["suit"];
                new_card.value = (int)parsedJsonResponse["cpu_hand"][i]["value"];
                if (new_card.value == 14)
                {
                    new_card.value = 1;
                }
                int multiplier = suitToNumber(new_card);
                GameObject new_playerCard = Instantiate(cardsArray[multiplier * 13 + new_card.value], new Vector3(-50 + i * 100, 0, 0), Quaternion.identity);
                new_playerCard.transform.SetParent(OpponentArea.transform, false);
            }
            SceneManager.LoadScene("RoundFinish", LoadSceneMode.Additive);
        }
    }

    public void deleteCards()
    {
        foreach(var card in GameData.drawn_cards)
        {
            if (card != null)
            {
                Destroy(card.instance);
            }
        }
    }

    public void updatePrices()
    {

        moneyPool.text = string.Format("Pula Pieniędzy: {0}", GameData.money_pool);
        playerTotal.text = string.Format("Pieniądze: {0}", GameData.player_total);
        playerPut.text = string.Format("Kwota Zakładu: {0}", GameData.player_put);
        opponentPut.text = string.Format("Kwota Zakładu: {0}", GameData.opponent_put);
        opponentTotal.text = string.Format("Pieniędze: {0}", GameData.opponent_total);
    }

    public int suitToNumber(Card c)
    {
        if (c.suit == "c")
        {
            return 0;
        }
        if(c.suit == "d")
        {
            return 1;
        }
        if (c.suit == "h")
        {
            return 2;
        }
        if (c.suit == "s")
        {
            return 3;
        }
        return -1;
    }
}
