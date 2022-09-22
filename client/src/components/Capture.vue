<template>
  <div class="mx-auto max-w-7xl sm:px-6 lg:px-8">
    <div class="bg-white">
      <div class="mx-auto max-w-7xl py-16 px-4 sm:py-24 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-lg font-semibold text-indigo-600">
            NailBiter AI Trainer
          </h2>
          <p
            class="mt-1 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl"
          >
            Capture Instructions.
          </p>
          <p class="mx-auto mt-5 max-w-xl text-xl text-gray-500">
            Select desired gesture.
          </p>
          <p class="mx-auto mt-5 max-w-xl text-xl text-gray-500">
            Get into position!
          </p>
          <p class="mx-auto mt-5 max-w-xl text-xl text-gray-500">
            Spacebar or click Button to start
          </p>
        </div>
        <p><strong>Details</strong></p>
        <p>
          For posing, you can just take normal pictures of your face when
          selecting no-bite but for bite you can just "simulate" nail biting by
          putting your fingers in/near/around your mouth as if you were biting
          them.
        </p>
        <br />
        <div class="inline-flex items-center">
          <button
            type="button"
            class="inline-flex items-center place-items-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            v-if="interval != null"
            v-on:click="stopCapture()"
          >
            Stop
          </button>
          <button
            type="button"
            class="inline-flex items-center place-items-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            v-else
            v-on:click="startCapture()"
          >
            Start
          </button>
          <div v-if="interval != null">Click Button or Spacebar to Stop!</div>
        </div>
      </div>
    </div>
    <fieldset class="mt-4">
      <legend class="sr-only">Notification method</legend>
      <div class="space-y-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-10">
        <div
          v-for="(item, index) in labels"
          :key="item + index"
          class="flex items-center"
        >
          <input
            :id="item"
            name="action"
            :value="item"
            type="radio"
            v-model="selectedAction"
            :checked="selectedAction == item"
            class="h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <label
            :for="item"
            class="ml-3 block text-sm font-medium text-gray-700"
            >{{ item }}</label
          >
        </div>
      </div>
    </fieldset>

    <div class="overflow-hidden rounded-lg bg-white shadow">
      <div class="px-4 py-5 sm:p-6">
        <div class="inline-flex flex-col items-center">
          <vue-web-cam
            id="video"
            ref="webcam"
            :device-id="deviceId"
            width="100%"
            @started="onStarted"
            @stopped="onStopped"
            @error="onError"
            @cameras="onCameras"
            @camera-change="onCameraChange"
          />

          <select
            v-model="camera"
            class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          >
            <option>-- Select Device --</option>
            <option
              v-for="device in devices"
              :key="device.deviceId"
              :value="device.deviceId"
            >
              {{ device.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
    <div class="overflow-hidden rounded-lg bg-white shadow">
      <div class="px-4 py-5 sm:p-6">
        <div id="listOPics" v-if="list.length > 0">
          <div>
            Click on an image to remove (or
            <button type="button" class="inline-flex items-center place-items-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-small text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2" v-on:click="clearImages()">Clear All</button>)
          </div>
          <div>
            (Also maybe clean out any images that might be ambiguous if
            possible)
          </div>
          <div id="warning" v-if="list.length >= 64">
            64 Limit Reached - either submit or remove some images
          </div>
          <ul role="list" class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 sm:gap-x-6 lg:grid-cols-4 xl:gap-x-8">
            <li v-for="(item, index) in list" :key="index" class="relative" @click="removeImage(index)">
              <div class="group aspect-w-10 aspect-h-7 block w-full overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                <img :src="item.image" alt="" class="pointer-events-none object-cover group-hover:opacity-75" />
              </div>
              <p class="pointer-events-none mt-2 block truncate text-sm font-medium text-gray-900">{{ item.type }}</p>
            </li>
          </ul>
          <div class="btn inline-flex items-center place-items-center rounded-md border border-transparent bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
            <button
              type="button"
              v-if="list.length > 0"
              v-on:click="submitImages()"
              v-show="!processing"
            >
              Submit Training Data
            </button>
          </div>
        </div>
        <div
          id="notifications"
          v-show="processing"
          v-on:click="processing = !processing"
        >
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { WebCam } from "vue-web-cam";

export default {
  name: "Capture",
  components: {
    "vue-web-cam": WebCam,
  },
  data: function () {
    return {
      processing: false,
      message: "",
      video: null,
      canvas: null,
      selectedAction: "no-face",
      list: [],
      lastresponse: null,
      interval: null,
      model: null,
      modelmeta: null,
      labels: ["no-face", "bite", "no-bite"],
      modelLabels: [],
      probabilities: [],
      guess: "no-face",
      vdim: {
        width: 0,
        height: 0,
      },
      appSettings: "",
      camera: null,
      deviceId: null,
      devices: [],
    };
  },
  computed: {
    device: function () {
      return this.devices.find((n) => n.deviceId === this.deviceId);
    },
  },
  watch: {
    camera: function (id) {
      this.deviceId = id;
    },
    devices: function () {
      // Once we have a list select the first one
      const [first] = this.devices;
      if (first) {
        this.camera = first.deviceId;
        this.deviceId = first.deviceId;
      }
    },
  },
  mounted: async function () {
    // map spacebar key event
    document.onkeyup = this.key;

    this.video = document.getElementById("video");

    // load appSettings
    let response = await axios.get("config.json");
    this.appSettings = response.data;
    console.log(this.appSettings);
  },
  methods: {
    onCapture() {
      this.$refs.webcam.capture();
    },
    onStarted(stream) {
      console.log("On Started Event", stream);
    },
    onStopped(stream) {
      console.log("On Stopped Event", stream);
    },
    onStop() {
      this.$refs.webcam.stop();
    },
    onStart() {
      this.$refs.webcam.start();
    },
    onError(error) {
      console.log("On Error Event", error);
    },
    onCameras(cameras) {
      this.devices = cameras;
      console.log("On Cameras Event", cameras);
    },
    onCameraChange(deviceId) {
      this.deviceId = deviceId;
      this.camera = deviceId;
      console.log("On Camera Change Event", deviceId);
    },
    key: function (event) {
      if (event.keyCode == 32) {
        if (this.interval != null) this.stopCapture();
        else this.startCapture();
      }
    },
    startCapture: function () {
      this.stopCapture();
      setTimeout(this.stopCapture, 60010);
      this.interval = setInterval(this.addImage, 500);
      this.video.style.border = "thick solid #FF0000";
    },
    stopCapture: function () {
      if (this.interval != null) {
        clearInterval(this.interval);
        this.interval = null;
        this.video.style.border = "solid 1px gray";
      }
    },
    addImage: function () {
      if (this.list.length < 64) {
        var cap = this.$refs.webcam.capture();
        this.list.push({
          type: this.selectedAction,
          image: cap,
        });
      } else {
        // reached max
        this.stopCapture();
      }
    },
    removeImage: function (index) {
      this.list.splice(index, 1);
    },
    clearImages: function () {
      this.list = [];
      this.processing = false;
    },
    submitImages: async function () {
      this.processing = true;
      this.message = "sending data";
      // api endpoint
      try {
        let url = this.appSettings.saveEndpoint;
        let max_submit = this.appSettings.maxSubmitCount;

        for (let i = 0; i < this.list.length; i += max_submit) {
          let response = await axios.post(
            url,
            { items: this.list.slice(i, i + max_submit) },
            {
              headers: { "Content-Type": "application/json" },
            }
          );
          this.lastresponse = response["data"];
        }

        this.message = "done!";
        this.list = [];
        this.processing = false;
      } catch (error) {
        // uh oh - log error and reset
        console.log(error);
        alert(error);
        this.processing = false;
      }
    },
  },
};
</script>

<style scoped>
#instructions {
  width: 640px;
  margin: 0px auto;
  text-align: left;
}
video {
  border: solid 1px gray;
  transform: rotateY(180deg);
  -webkit-transform: rotateY(180deg); /* Safari and Chrome */
  -moz-transform: rotateY(180deg); /* Firefox */
  float: left;
}

#output {
  border: solid 1px gray;
  height: 240px;
  width: 320px;
  margin-left: 10px;
  float: right;
  clear: right;
  text-align: left;
  padding: 0px 4px;
}

#videoPane {
  float: left;
  height: 275px;
}

#deviceOptions {
  margin-top: 20px;
  padding: 10px;
}

#images {
  margin: 0px auto;
  width: 700px;
  /* border: solid 10px red;*/
}

#triggerButton {
  width: 40pt;
  height: 40pt;
}

#rendered {
  display: none;
}

#canvas {
  display: none;
}
#warning {
  color: red;
  font-size: 16px;
  font-weight: bold;
}
#listOPics {
  clear: both;
  padding: 25px 100px;
  text-align: center;
  margin: 0px;
}
#radioselection {
  margin-bottom: 10px;
}

#notifications {
  width: 150px;
  height: 30px;
  display: table-cell;
  text-align: center;
  background: rgb(255, 166, 0);
  border: 1px solid #000;
  bottom: 10px;
  right: 10px;
  position: absolute;
  padding-top: 10px;
}

.imagelist {
  list-style-type: none;
  padding: 0px;
}

.imgitem {
  float: left;
  padding: 10px;
}

.btn {
  text-align: center;
  clear: both;
}
#plist ul {
  margin: 1px;
}
#plist li {
  /*border: solid 1px black;*/
  margin: 5px;
}

#current {
  text-align: center;
  margin: 3px;
  font-size: 30px;
  color: red;
  font-weight: bolder;
}

#flavor {
  margin-top: 5px;
  margin-bottom: 5px;
}

#exported {
  margin-bottom: 5px;
}
#console {
  margin: 20px;
}
</style>
