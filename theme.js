import { future } from "mdx-deck/themes";
import darcula from "react-syntax-highlighter/styles/prism/darcula";
import python from "react-syntax-highlighter/languages/prism/python";
import js from "react-syntax-highlighter/languages/prism/javascript";

export default {
  ...future,
  prism: {
    style: darcula,
    languages: {
      python: python,
      javascript: js
    }
  }
};
