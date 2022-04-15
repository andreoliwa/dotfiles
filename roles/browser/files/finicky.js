// https://github.com/johnste/finicky
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
    {
      // Work URLs
      // Match any part of the URL with the regexes below
      match: [
        /localhost/,

        // Wolt
        /ops.wolt/,
        /@wolt/,
        /woltapp/,
        /k.wolt.com/,
        /creditornot/,
        /planitpoker/,
        /liveshare/,
        /wo.lt/,
        /woltapi/,
        /vipps/,
        /docs.google.com/,
        /drive.google.com/,
        /retrium.com/,
        /kotlin/,
        /ktlint/,
        /java.com/,
        /baeldung/,
        /java.net/,
        /jooq.org/,
        /spring/, // Not the season of the year, but the Java framework
        /postman.com/,
        /snowflake.com/,
        /maven/,
        /mvn/,
        /gradle/,
        /kube/,
        /kaf/,
        /apache/,
        /protocol-buffers/,
        /confluentinc/,
        /jenkins/,
        /grafana/,

        // sennder
        /sennder/,
        /atlassian/,
        /slack/,
        /datadog/,
        /aws/,
        /awsapps.com/,
        /amazon.com/,
        /thoughtworks/,
        /martinfowler/,
        /salesforce/,
        /invisionapp.com/,
        /asana.com/,
        /miro.com/,
        /jetbrains.com/,
        /pardot.com/,
        /sentry.io/,
        /sli.do/,

        // EatFirst
        /eatfirst/,
        /zulip/,
        /dashlane/,
        /adyen/,
        /cloudflare/,
        /newrelic/,
        /terraform/,

        // B2BFG
        /makeeathappen/,
        /b2bfood.group/,
        /lemoncat/,
        /caterwings/,
        /caterdesk/,
        /orderin/,
        /algolia/,
      ],
      browser: "Brave Browser",
    },
    {
      match: finicky.matchDomains([
        /eatfirst\.(ninja|com)$/,
        "trello.com",
        "meet.google.com",
        "force.com",
        /.*atlassian\.(com|net)$/,
        /.*atl-paas.net/,
      ]),
      browser: "Brave Browser",
    },
    // Work parameters on the query string
    {
      match: ({ url }) => url.search.includes(["sennder", "eatfirst"]),
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
