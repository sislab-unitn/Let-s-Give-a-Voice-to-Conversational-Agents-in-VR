// using System.Collections;
// using UnityEngine;
// using UnityEngine.Events;
// using UnityEngine.Networking;
// using UnityEngine.UI;
// /// <summary>
// /// This class is used to connect to a server and send a request to get a stream of audio data
// /// </summary>
// public class ServerConnectionStream : ServerConnection
// {
//     #region Editor Exposed Variables
//     /// <summary>
//     /// input audio sample rate
//     /// <summary>
//     [Tooltip("input audio sample rate")]
//     public int inputSampleRate;
//     /// <summary>
//     /// output audio sample rate
//     /// <summary>
//     [Tooltip("output audio sample rate")]
//     public int outputSampleRate;
//     /// <summary>
//     /// Set a Button to enable sending the audio file
//     /// </summary>
//     [Tooltip("Set a Button to enable sending the audio file")]
//     public Button SendButton;
//     /// <summary>
//     /// Set the outputsource
//     /// <summary>
//     [Tooltip("audiosource from where to play the response")]
//     public AudioSource outputSource;
//     #endregion

//     /// <summary>
//     /// Recorded clip
//     /// <summary>
//     private AudioClip clip;
//     private int maxRecordingTime = 300;
    
//     // Start is called before the first frame update. It inherits from ServerConnection

//     // Update is called once per frame
//     void Update()
//     {

//     }
//     public void buttonClicked()
//     {
//         if (!this.clip.isRecording)
//         {
//             StartRecording();
//         }
//         else
//         {
//             StopRecording();
//             SendAndPlay();
//         }
//     }
//     public void StartRecording()
//     {
//         this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
//         this.isRecording = true;
//     }
//     public void StopRecording()
//     {
//         var position = Microphone.GetPosition(Microphone.devices[0]);
//         Microphone.End(Microphone.devices[0]);
//         this.isRecording = false;
//         this.clip = Audio.trimAudioClip(this.clip, position);

//     }
//     public void SendAndPlay()
//     {
//         requestStarted.Invoke();
//         StartCoroutine(PostStreamAndPlay());
//     }


//     protected IEnumerator PostStreamAndPlay()
//     {
//         byte[] fileContent = Audio.ConvertWav(this.clip);
//         UnityWebRequest request = new UnityWebRequest(this.url, "POST");
//         UploadHandler uploader = new UploadHandlerRaw(fileContent);
//         // the download handler is a custom one that automatically plays the audio in streaming mode
//         StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate,1);
//         request.uploadHandler = uploader;
//         request.downloadHandler = downloader;
//         request.SetRequestHeader("Content-Type", "audio/wav");
//         yield return request.SendWebRequest();
//         if (request.result != UnityWebRequest.Result.Success)
//         {
//             Debug.Log(request.error);
//         }
//         else
//         {
//             requestDone.Invoke();
//         }
//         yield return null;
//     }
//     // This comes from SoundWav module


// }
