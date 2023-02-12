﻿using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine.Events;
using static UnityEngine.JsonUtility;
using UnityEditor;
namespace Recorder
{
    /// <summary>
    /// Add this component to a GameObject to Record Mic Input 
    /// </summary>
    [AddComponentMenu("AhmedSchrute/Recorder")]
    [RequireComponent(typeof(AudioSource))]
    public class Recorder : MonoBehaviour
    {
        #region Constants &  Static Variables
        /// <summary>
        /// Audio Source to store Microphone Input, An AudioSource Component is required by default
        /// </summary>
        static AudioSource audioSource;
        /// <summary>
        /// The samples are floats ranging from -1.0f to 1.0f, representing the data in the audio clip
        /// </summary>
        static float[] samplesData;
        /// <summary>
        /// WAV file header size
        /// </summary>
        const int HEADER_SIZE = 44;
        bool isRecording = false;
        public UnityEvent myEvent = new UnityEvent();
        #endregion

        #region Editor Exposed Variables

        /// <summary>
        /// Set a keyboard key for saving the Audio File
        /// </summary>
        [Tooltip("Set a keyboard key for saving the Audio File")]
        public KeyCode keyCode;
        /// <summary>
        /// Set a Button to trigger writing the WAV file and Saving the Audio 
        /// </summary>
        public Button SaveButton;
        /// <summary>
        /// What should the saved file name be, the file will be saved in Streaming Assets Directory
        /// </summary>
        [Tooltip("What should the saved file name be, the file will be saved in Streaming Assets Directory, Don't add .wav at the end")]
        public string fileName;
        /// <summary>
        /// The URL to post the audio file to
        /// </summary>
        [Tooltip("The URL to post the audio file to")]
        public string url;

        #endregion

        #region MonoBehaviour Callbacks

        void Start()
        {
            foreach (var device in Microphone.devices)
            {
                Debug.Log("Name: " + device);
            }
            audioSource = GetComponent<AudioSource>();
            //audioSource.clip = Microphone.Start(Microphone.devices[0], true, 10, 44100);
            if (SaveButton == null)
            {
                return;
            }
            SaveButton.onClick.AddListener(() =>
            {
                if (!isRecording){
                    audioSource.clip = Microphone.Start(Microphone.devices[0], true, 10, 44100);
                    isRecording = true;
                    //SaveButton.GetComponentInChildren<Text>().text = "Recording...";
                }else {
                    //Microphone.End(Microphone.devices[0]);
                    isRecording = false;
                    Save(fileName);
                    Microphone.End(Microphone.devices[0]);
                    // disable save button
                    SaveButton.interactable = false;
                    StartCoroutine(postRequest());
                }
            });
        }

        private void Update()
        {
            if (Input.GetKeyDown(keyCode))
            {
                if (!isRecording){
                    audioSource.clip = Microphone.Start(Microphone.devices[0], true, 10, 44100);
                    isRecording = true;
                    //SaveButton.GetComponentInChildren<Text>().text = "Recording...";
                }else {
                    //Microphone.End(Microphone.devices[0]);
                    isRecording = false;
                    Save(fileName);
                    Microphone.End(Microphone.devices[0]);
                    SaveButton.interactable = false;
                    StartCoroutine(postRequest());

                }
            }
        }


        #endregion

        #region Recorder Functions

        public static void Save(string fileName = "test")
        {

            while (!(Microphone.GetPosition(null) > 0)) { }
            samplesData = new float[audioSource.clip.samples * audioSource.clip.channels];
            audioSource.clip.GetData(samplesData, 0);
            string filePath = Path.Combine("Assets/Kumo", fileName + ".wav");
            // Delete the file if it exists.
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }
            try
            {
                WriteWAVFile(audioSource.clip, filePath);
                Debug.Log("File Saved Successfully at Kumo/" + fileName + ".wav");
            }
            catch (DirectoryNotFoundException)
            {
                Debug.LogError("Please, Create a Kumo Directory in the Assets Folder");
            }
           
        }

        IEnumerator postRequest()
        {
            byte [] fileContent= File.ReadAllBytes("Assets/Kumo/"+fileName+".wav");
            string content = System.Convert.ToBase64String(fileContent);
            // log the result
            Debug.Log("here");
            // create a request with json
            string json = "{\"sender\":\"Unity\",\"audio\": \""+content+"\"}";
            UnityWebRequest request = UnityWebRequest.Put(url,json);
            request.SetRequestHeader("Content-Type", "application/json");
            yield return request.SendWebRequest();
            if (request.result != UnityWebRequest.Result.Success) {
                Debug.Log(request.error);
            }
            else {
                Debug.Log("Upload complete!");
                // save the result as binary
                // parse back the result
                //Dictionary<string,string> data = JsonConvert.DeserializeObject<Dictionary<string, string>>(request.downloadHandler.text);
                //ConversationData data = JsonConvert.DeserializeObject(request.downloadHandler.text, typeof(ConversationData)) as ConversationData;
                ConversationData data = (ConversationData) JsonUtility.FromJson(request.downloadHandler.text, typeof(ConversationData));
                // audio = System.Convert.FromBase64String(data.audio);
                // GetComponent<AudioSource>().getAudioClip();
                File.WriteAllBytes("Assets/Kumo/"+"response"+".wav", System.Convert.FromBase64String(data.audio));
                AssetDatabase.Refresh();
                // wait for the next frame
                // play the audio

                myEvent.Invoke();
            }
            
            SaveButton.interactable = true;
        }

        // WAV file format from http://soundfile.sapp.org/doc/WaveFormat/
        static void WriteWAVFile(AudioClip clip, string filePath)
        {
            float[] clipData = new float[clip.samples];

            //Create the file.
            using (Stream fs = File.Create(filePath))
            {
                int frequency = clip.frequency;
                int numOfChannels = clip.channels;
                int samples = clip.samples;
                fs.Seek(0, SeekOrigin.Begin);

                //Header

                // Chunk ID
                byte[] riff = Encoding.ASCII.GetBytes("RIFF");
                fs.Write(riff, 0, 4);

                // ChunkSize
                byte[] chunkSize = BitConverter.GetBytes((HEADER_SIZE + clipData.Length) - 8);
                fs.Write(chunkSize, 0, 4);

                // Format
                byte[] wave = Encoding.ASCII.GetBytes("WAVE");
                fs.Write(wave, 0, 4);

                // Subchunk1ID
                byte[] fmt = Encoding.ASCII.GetBytes("fmt ");
                fs.Write(fmt, 0, 4);

                // Subchunk1Size
                byte[] subChunk1 = BitConverter.GetBytes(16);
                fs.Write(subChunk1, 0, 4);

                // AudioFormat
                byte[] audioFormat = BitConverter.GetBytes(1);
                fs.Write(audioFormat, 0, 2);

                // NumChannels
                byte[] numChannels = BitConverter.GetBytes(numOfChannels);
                fs.Write(numChannels, 0, 2);

                // SampleRate
                byte[] sampleRate = BitConverter.GetBytes(frequency);
                fs.Write(sampleRate, 0, 4);

                // ByteRate
                byte[] byteRate = BitConverter.GetBytes(frequency * numOfChannels * 2); // sampleRate * bytesPerSample*number of channels, here 44100*2*2
                fs.Write(byteRate, 0, 4);

                // BlockAlign
                ushort blockAlign = (ushort)(numOfChannels * 2);
                fs.Write(BitConverter.GetBytes(blockAlign), 0, 2);

                // BitsPerSample
                ushort bps = 16;
                byte[] bitsPerSample = BitConverter.GetBytes(bps);
                fs.Write(bitsPerSample, 0, 2);

                // Subchunk2ID
                byte[] datastring = Encoding.ASCII.GetBytes("data");
                fs.Write(datastring, 0, 4);

                // Subchunk2Size
                byte[] subChunk2 = BitConverter.GetBytes(samples * numOfChannels * 2);
                fs.Write(subChunk2, 0, 4);

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
                
                fs.Write(bytesData, 0, bytesData.Length);
            }
        }

        #endregion
    }
}