using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;

using System;
using System.IO;
using System.Threading;


public class AgentTalk: MonoBehaviour
{
    private string avatar_responses_path = "avatar_responses/";
    private string intro = "presentation";
    private string bye = "bye";

    private string[] amt_files = {"Amicizia", "Colpa", "Entusiasmo", "Fallimento", "Felicita", "Malattia", "Preoccupazione", "Sorriso", "Tristezza"};
    private string[] usom_files = {"usom_negative", "usom_positive"};

    public string host = "localhost";
    public string port = "8000";
    public string ner_path = "ner";

    public int outputSampleRate = 24000;

    public void PlayIntro(AudioSource source, UnityEvent presDone)
    {
        string path = avatar_responses_path + intro;
        UnityEngine.Debug.Log(path);
        StartCoroutine(PlayAndRecord(source, path, presDone));
    }

    IEnumerator PlayAndRecord(AudioSource source, string file, UnityEvent presDone)
    {
        AudioClip audioClip = Resources.Load<AudioClip>(file);
        source.PlayOneShot(audioClip);

        while (source.isPlaying)
        {
            yield return null;
        }
        presDone.Invoke();
        yield return null;
    }

    public void PlayBye(AudioSource source)
    {
        string path = avatar_responses_path + bye;
        UnityEngine.Debug.Log(path);
        PlayFile(source, path);

    }

    private void PlayFile(AudioSource source, string file)
    {
        AudioClip audioClip = Resources.Load<AudioClip>(file);
        source.PlayOneShot(audioClip);
    }

    public void Greet(AudioSource source, AudioClip clip, UnityEvent presDone)
    {
        UnityEngine.Debug.Log("start post");
        StartCoroutine(PostNER(source, clip, presDone));
    }

    IEnumerator PostNER(AudioSource source, AudioClip clip, UnityEvent presDone)
    {
        byte[] fileContent = Audio.ConvertWav(clip);
        UnityEngine.Debug.Log("Byte content");
        UnityEngine.Debug.Log(fileContent.Length);

        string url = "http://" + this.host + ":" + this.port + "/" + this.ner_path;

        UnityWebRequest request = new UnityWebRequest(url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);

        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(source, this.outputSampleRate, 1, pauseLength: 100);
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            UnityEngine.Debug.Log(request.error);
        }
        else
        {
            source.Play();
        }
        while (source.isPlaying)
        {
            yield return null;
        }
        PlayRandomMessage(source);
        while (source.isPlaying)
        {
            yield return null;
        }
        presDone.Invoke();
        yield return null;
    }

    private void PlayRandomMessage(AudioSource source)
    {
        System.Random random = new System.Random();
        int randomValue = random.Next(2); 
        UnityEngine.Debug.Log(randomValue);
        string randomFile;

        if (randomValue==0) {
            int randomIndex = random.Next(amt_files.Length);
            randomFile = amt_files[randomIndex];
            randomFile = avatar_responses_path + "amt/" + randomFile;
        }
        else {
            int randomIndex = random.Next(usom_files.Length);
            randomFile = usom_files[randomIndex];
            randomFile = avatar_responses_path + "usom/" + randomFile;        
        }

        // randomFile = avatar_responses_path + "amt/Entusiasmo";

        PlayFile(source, randomFile);
        
        UnityEngine.Debug.Log(randomFile);

    }

    void Start()
    {

    }

    void Update()
    {

    }

}
