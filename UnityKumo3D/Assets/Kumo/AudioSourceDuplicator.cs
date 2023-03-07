
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
public class AudioSourceDuplicator : MonoBehaviour{
    #region Editor Exposed Variables
    public AudioSource audioSource;
    public AudioSource audioDestination;
    #endregion
    void Start()
    {

    }
    void Update()
    {
    }
    public void DuplicateAudioSource()
    {
        this.audioDestination.clip =  Audio.duplicateAudioClip(this.audioSource.clip);
    }
}