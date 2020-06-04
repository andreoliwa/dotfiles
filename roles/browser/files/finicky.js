module.exports = {
  // Using the unstable browser for personal purposes, and the stable one for work
  defaultBrowser: "Brave Browser Dev",
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
          .filter((part) => !part.startsWith("utm_"));
        return {
          ...url,
          search: search.join("&"),
        };
      },
    },
  ],
  handlers: [
    // Work URLs
    {
      match: [
        /eatfirst/,
        /zulip/,
        /dashlane/,
        /makeeathappen/,
        /b2bfood.group/,
        /lemoncat/,
        /caterwings/,
        /caterdesk/,
        /aws.amazon.com/,
        /orderin/,
        /algolia.com/,
        /adyen.com/,
        /salesforce.com/,
        /force.com/,
        /cloudflare.com/,
        /newrelic.com/,
      ],
      browser: "Brave Browser",
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
        /.*atl-paas.net/,
      ]),
      browser: "Brave Browser",
    },
    // Work apps
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#matching-an-array-of-multiple-apps
      // https://github.com/johnste/finicky#advanced-usage
      match: ({ sourceBundleIdentifier }) =>
        [
          // Slack
          "com.tinyspeck.slackmacgap",
        ].includes(sourceBundleIdentifier),
      browser: "Brave Browser",
    },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#open-spotify-links-in-spotify-app
      match: finicky.matchDomains("open.spotify.com"),
      browser: "Spotify",
    },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#open-zoom-links-in-zoom-app
      match: /zoom.us\/j\//,
      browser: "us.zoom.xos",
    },
  ],
};
// For more examples, see the Finicky github page https://github.com/johnste/finicky
