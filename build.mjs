import * as esbuild from "esbuild";

await esbuild.build({
  entryPoints: ["src/App.jsx"],
  bundle: true,
  minify: true,
  sourcemap: false,
  target: ["es2019"],
  outfile: "assets/js/bundle.js",
  define: { "process.env.NODE_ENV": '"production"' },
  loader: { ".jsx": "jsx" },
  jsx: "automatic",
  legalComments: "none",
});
console.log("build ok");
