/// <reference types="react" />

// This ensures the global JSX namespace is available, for 3rd party libs
import * as React from 'react';
declare global {
  namespace JSX {
    interface IntrinsicElements extends React.JSX.IntrinsicElements {}
  }
}