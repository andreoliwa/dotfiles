module.exports = {
  defaultBrowser: "Brave Browser",
  rewrite: [
    // {
    //   // https://github.com/johnste/finicky/wiki/Configuration-ideas#force-https-for-all-urls
    //   match: ({ url }) => url.protocol === "http" && url.host != "localhost",
    //   url: ({ url }) => ({
    //     ...url,
    //     protocol: "https"
    //   })
    // },
    // {
    //   // https://github.com/johnste/finicky/wiki/Configuration-ideas#redirect-google-links-to-duckduckgocom
    //   match: finicky.matchDomains([/google\.(com|de|com.br|.+)$/]),
    //   url: ({ url }) => ({
    //     ...url,
    //     host: "duckduckgo.com"
    //   })
    // },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#remove-all-marketingtracking-information-from-urls
      match: ({ url }) => url.search.includes("utm_"),
      url: ({ url }) => {
        const search = url.search
          .split("&")
          .filter(part => !part.startsWith("utm_"));
        return {
          ...url,
          search: search.join("&")
        };
      }
    }
  ],
  handlers: [
    // Work URLs
    {
      match: [/\/eatfirst/, /\/makeeathappen/, /\/b2bfood.group/],
      browser: "Vivaldi"
    },
    {
      match: finicky.matchDomains([
        /eatfirst\.(ninja|com)$/,
        "trello.com",
        "meet.google.com",
        "terraform.io",
        "dashlane.com",
        /.*slack.com/,
        /.*atlassian\.(com|net)$/,
        /.*atl-paas.net/
      ]),
      browser: "Vivaldi"
    },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#open-spotify-links-in-spotify-app
      match: finicky.matchDomains("open.spotify.com"),
      browser: "Spotify"
    }
  ]
};
// For more examples, see the Finicky github page https://github.com/johnste/finicky
