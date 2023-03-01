using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using UnityEditor;
using System;
using System.Globalization;
using System.Text;
using System.Threading;
public class ServerConnectionStream : MonoBehaviour
{

    string url;

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
    /// Set a Button to enable sending the audio file
    /// </summary>
    ///[Tooltip("Set a Button to enable sending the audio file")]
    public Button SendButton;
    #endregion
    public UnityEvent requestStarted = new UnityEvent();
    public UnityEvent requestDone = new UnityEvent();
    // Start is called before the first frame update

    public AudioSource inputSource;
    public AudioSource outputSource;
    private bool isRecording = false;
    private AudioClip clip;
    const int HEADER_SIZE = 44;
    void Start()
    {
        url = (ssl ? "https://" : "http://") + host + ((port != "") ? ":" + port : "");
        UnityWebRequest request = UnityWebRequest.Get(url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Connection Successful!");
        }
        url = url + "/" + path + "?sender=" + sender_id;
    }

    // Update is called once per frame
    void Update()
    {

    }
    public void buttonClicked()
    {
        if (!isRecording)
        {
            StartRecording();
        }
        else
        {
            StopRecording();
            SendAndPlay();
        }
    }
    public void StartRecording()
    {
        inputSource.clip = Microphone.Start(Microphone.devices[0], true, 300, 44100);
        isRecording = true;
    }
    public void StopRecording()
    {
        var position = Microphone.GetPosition(Microphone.devices[0]);
        Microphone.End(Microphone.devices[0]);
        isRecording = false;
        inputSource.clip = trimAudioClip(inputSource.clip, position);
        
    }
    public void SendAndPlay()
    {
        requestStarted.Invoke();
        StartCoroutine(PostStreamAndPlayStream(url, inputSource.clip));
    }
    private AudioClip trimAudioClip(AudioClip clip, int position)
    {

        var soundData = new float[clip.samples * clip.channels];
        clip.GetData(soundData, 0);
        var newData = new float[position * clip.channels];
        for (int i = 0; i < newData.Length; i++)
        {
            newData[i] = soundData[i];
        }
        var newClip = AudioClip.Create(clip.name,position,clip.channels,clip.frequency,false,false);
        newClip.SetData(newData, 0);
        return newClip;
    }

    private AudioClip LoadClip(byte [] receivedBytes)
    {
        List<float> f_decoding = new List<float>();
 
        for (int i = 0; i < receivedBytes.Length; i += 2)
        {
            int sample = BitConverter.ToInt16(receivedBytes, i);
            f_decoding.Add(sample / 32768.0f);
            // if (f_decoding.Count == 16000 * 1)
            // {
            //     yield return null;
            // }
        }
       
        int channels = 1;
        int sampleRate = 16000;
        AudioClip clip = AudioClip.Create("Response", f_decoding.Count, channels, sampleRate, false);
        clip.SetData(f_decoding.ToArray(), 0);
 
        return clip;
    }
    IEnumerator PostStreamAndPlayStream(string url, AudioClip clip)
    {
        byte[] fileContent = ConvertWav(clip);
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);
        DownloadHandler downloader = new DownloadHandlerBuffer();
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        request.chunkedTransfer = true;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Upload complete!");
            byte[] receivedBytes = request.downloadHandler.data;
            outputSource.clip = LoadClip(receivedBytes);
            outputSource.PlayOneShot( outputSource.clip);
            requestDone.Invoke();
        }

    }

    IEnumerator PostStreamAndPlay(string url, AudioClip clip)
    {
        byte[] fileContent = ConvertWav(clip);
        UnityWebRequest request = new UnityWebRequest(url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);
        DownloadHandlerAudioClip downloader = new DownloadHandlerAudioClip(url, AudioType.WAV);
        downloader.streamAudio = true;
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        request.chunkedTransfer = true;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Upload complete!");
            outputSource.PlayOneShot(DownloadHandlerAudioClip.GetContent(request));
            requestDone.Invoke();
        }

    }
 // This comes from SoundWav module
    static byte[] ConvertWav(AudioClip clip)
    {

        byte[] arr = new byte[44];

        float[] clipData = new float[clip.samples];
        int frequency = clip.frequency;
        int numOfChannels = clip.channels;
        int samples = clip.samples;
        //Header
        
        // Chunk ID
        byte[] riff = Encoding.ASCII.GetBytes("RIFF");
        Array.Copy(riff, 0, arr, 0, 4);
        // ChunkSize
        byte[] chunkSize = BitConverter.GetBytes((HEADER_SIZE + clipData.Length) - 8);
        Array.Copy(chunkSize, 0, arr, 4, 4);
        // Format
        byte[] wave = Encoding.ASCII.GetBytes("WAVE");
        Array.Copy(wave, 0, arr, 8, 4);
        // Subchunk1ID
        byte[] fmt = Encoding.ASCII.GetBytes("fmt ");
        Array.Copy(fmt, 0, arr, 12, 4);
        // Subchunk1Size
        byte[] subChunk1 = BitConverter.GetBytes(16);
        Array.Copy(subChunk1, 0, arr, 16, 4);
        // AudioFormat
        byte[] audioFormat = BitConverter.GetBytes(1);
        Array.Copy(audioFormat, 0, arr, 20, 2);
        // NumChannels
        byte[] numChannels = BitConverter.GetBytes(numOfChannels);
        Array.Copy(numChannels, 0, arr, 22, 2);
        // SampleRate
        byte[] sampleRate = BitConverter.GetBytes(frequency);
        Array.Copy(sampleRate, 0, arr, 24, 4);
        // ByteRate
        byte[] byteRate = BitConverter.GetBytes(frequency * numOfChannels * 2); // sampleRate * bytesPerSample*number of channels, here 44100*2*2
        Array.Copy(byteRate, 0, arr, 28, 4);
        // BlockAlign
        ushort blockAlign = (ushort)(numOfChannels * 2);
        Array.Copy(BitConverter.GetBytes(blockAlign), 0, arr, 32, 2);
        // BitsPerSample
        ushort bps = 16;
        byte[] bitsPerSample = BitConverter.GetBytes(bps);
        Array.Copy(bitsPerSample, 0, arr, 34, 2);
        // Subchunk2ID
        byte[] datastring = Encoding.ASCII.GetBytes("data");
        Array.Copy(datastring, 0, arr, 36, 4);
        // Subchunk2Size
        byte[] subChunk2 = BitConverter.GetBytes(samples * numOfChannels * 2);
        Array.Copy(subChunk2, 0, arr, 40, 4);
        // Data

        clip.GetData(clipData, 0);
        short[] intData = new short[clipData.Length];
        byte[] bytesData = new byte[clipData.Length * 2];

        int convertionFactor = 32767;

        for (int i = 0; i < clipData.Length; i++)
        {
            intData[i] = (short)(clipData[i] * convertionFactor);
            byte[] byteArr = new byte[2];
            byteArr = BitConverter.GetBytes(intData[i]);
            byteArr.CopyTo(bytesData, i * 2);
        }
        // concatenate header and data
        byte[] final = new byte[arr.Length + bytesData.Length];
        arr.CopyTo(final, 0);
        bytesData.CopyTo(final, arr.Length);
        return final;
    }

}
