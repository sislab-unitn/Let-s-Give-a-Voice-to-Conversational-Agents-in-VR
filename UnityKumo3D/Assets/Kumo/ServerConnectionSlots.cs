using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using System;
using System.Globalization;
using System.Text;
using TMPro;
using LitJson;
public class ServerConnectionSlots : MonoBehaviour
{
    #region Editor Exposed Variables

    /// <summary>
    /// The host to post the audio file to
    /// </summary>
    [Tooltip("The host to post the audio file to")]
    public string host;
    /// <summary>
    /// The port to post the audio file to
    /// </summary>
    [Tooltip("The port to post the audio file to")]
    public string port;
    /// <summary>
    /// The path to post the audio file to
    /// </summary>
    [Tooltip("The path to post the audio file to")]
    public string path;
    /// <summary>
    /// The sender id for rasa to use
    /// </summary>
    [Tooltip("The sender id for rasa to use")]
    public string sender_id;
    /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl;

    /// <summary>
    public Image[] image;
    public TMP_Text[] text;
    public TMP_Text transcription;
    public TMP_Text response;
    #endregion
    private string url;
    void Start()
    {
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Connection Successful!");
        }
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
    }

    // Update is called once per frame
    void Update()
    {

        
    }

    public IEnumerator GetSlots()
    {
        UnityWebRequest request = new UnityWebRequest(this.url, "GET");
        // the download handler is a custom one that automatically plays the audio in streaming mode
        DownloadHandlerBuffer downloader = new DownloadHandlerBuffer();
        request.downloadHandler = downloader;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            
            JsonData data = JsonMapper.ToObject(request.downloadHandler.text);
            
            for (int i = 0; i < data.Count; i++)
            {
                try{
                    for (int j = 0; j < data["titles"].Count; j++)
                    {
                        text[j].text = data["titles"][j].ToString();
                    }
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
                try{
                    for (int j = 0; j < data["images"].Count; j++)
                    {
                        // decode bytes from base64
                        byte[] bytes = Convert.FromBase64String((data["images"][j].ToString()));
                        // save the bytes to a file
                        string path = Application.dataPath + "/Temp/" + "image_" +j + ".jpg";
                        File.WriteAllBytes(path, bytes);
                        Texture2D texture = new Texture2D(2, 2);
                        texture.LoadImage(bytes);
                        image[j].sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                    }
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
                try{
                    transcription.text = data["transcription"].ToString();
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                } 
                try{
                    response.text = data["response"].ToString();
        
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
            }
            Debug.Log("Slots Received!");
        }
        yield return null;
    }
    // This comes from SoundWav module


}
