"use client"
import React from "react";

const Loading = () => {
  return (
    <div className="loader">
      <style jsx>{`
        $colors: hsla(337, 84, 48, 0.75),
          hsla(160, 50, 48, 0.75),
          hsla(190, 61, 65, 0.75),
          hsla(41, 82, 52, 0.75);
        $size: 2.5em;
        $thickness: 0.5em;

        $lat: ($size - $thickness) / 2;
        $offset: $lat - $thickness;

        .loader {
          position: relative;
          width: 2.5em;
          height: 2.5em;
          transform: rotate(165deg);
        }

        .loader:before,
        .loader:after {
          content: '';
          position: absolute;
          top: 50%;
          left: 50%;
          display: block;
          width: 0.5em;
          height: 0.5em;
          border-radius: 50%;
          transform: translate(-50%, -50%);
        }

        .loader:before {
          animation: before 2s infinite;
        }

        .loader:after {
          animation: after 2s infinite;
        }

        @keyframes before {
          0% {
            width: 0.5em;
            box-shadow: 1em -0.75em hsla(337, 84%, 48%, 0.75),
              -1em 0.75em hsla(190, 61%, 65%, 0.75);
          }
          35% {
            width: 2.5em;
            box-shadow: 0 -0.75em hsla(337, 84%, 48%, 0.75),
              0 0.75em hsla(190, 61%, 65%, 0.75);
          }
          70% {
            width: 0.5em;
            box-shadow: -1em -0.75em hsla(337, 84%, 48%, 0.75),
              1em 0.75em hsla(190, 61%, 65%, 0.75);
          }
          100% {
            box-shadow: 1em -0.75em hsla(337, 84%, 48%, 0.75),
              -1em 0.75em hsla(190, 61%, 65%, 0.75);
          }
        }

        @keyframes after {
          0% {
            height: 0.5em;
            box-shadow: 0.75em 1em hsla(160, 50%, 48%, 0.75),
              -0.75em -1em hsla(41, 82%, 52%, 0.75);
          }
          35% {
            height: 2.5em;
            box-shadow: 0.75em 0 hsla(160, 50%, 48%, 0.75),
              -0.75em 0 hsla(41, 82%, 52%, 0.75);
          }
          70% {
            height: 0.5em;
            box-shadow: 0.75em -1em hsla(160, 50%, 48%, 0.75),
              -0.75em 1em hsla(41, 82%, 52%, 0.75);
          }
          100% {
            box-shadow: 0.75em 1em hsla(160, 50%, 48%, 0.75),
              -0.75em -1em hsla(41, 82%, 52%, 0.75);
          }
        }

        html,
        body {
          height: 100%;
        }

        .loader {
          position: absolute;
          top: calc(50% - 1.25em);
          left: calc(50% - 1.25em);
        }
      `}</style>
    </div>
  );
};

export default Loading;