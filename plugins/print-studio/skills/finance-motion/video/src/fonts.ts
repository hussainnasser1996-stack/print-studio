import {loadFont as anton} from "@remotion/google-fonts/Anton";
import {loadFont as archivo} from "@remotion/google-fonts/Archivo";
import {loadFont as newsreader} from "@remotion/google-fonts/Newsreader";
import {loadFont as spaceMono} from "@remotion/google-fonts/SpaceMono";

export const DISPLAY = anton("normal", {weights: ["400"], subsets: ["latin"]}).fontFamily;
export const SANS = archivo("normal", {weights: ["400", "600", "700", "800"], subsets: ["latin"]}).fontFamily;
export const SERIF = newsreader("italic", {weights: ["400"], subsets: ["latin"]}).fontFamily;
export const MONO = spaceMono("normal", {weights: ["400", "700"], subsets: ["latin"]}).fontFamily;
