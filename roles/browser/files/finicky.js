// TODO: is there a way to match handlers conditionally? e.g.: only when Slack is open
const today = new Date();
const dayOfWeek = today.getDay();
const isWeekend = dayOfWeek === 6 || dayOfWeek === 0;

// Work URLs
// Match any part of the URL with the regexes below
var workURLs = [
  // Wolt
  /ops.wolt/,
  /@wolt/,
  /woltapp/,
  /wolt\./,
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
  /postman.com/,
  /jfrog/,
  /doordash/,
  /okta/,
  /cuckooworkout/,
  /daas/,
  /oreilly/,
  /snowflake.com/,
  /accounts.google.com/,
  /AccountChooser/,
  /GlifWebSignIn/, // Snowflake OAuth login with https://accounts.google.com/AccountChooser/signinchooser
  /maven/,
  /mvn/,
  /gradle/,
  /kube/,
  /k8s/,
  /apache/,
  /protocol-buffers/,
  /confluentinc/,
  /jenkins/,
  /grafana/,
  /smartrecruiters.com/,
  /google.zoom/,
  /finaro/,
  /credorax/,
  /adp.com/,
  /workday/,
  /chime.aws/,
  /figma/,
  /phrase.com/,
  /tailscale/,
  /copilot/,
  /event.on24.com/,
  /kreya/,
  /scalyr/,
  /cursor./,
  /chatgpt/,
  /openai/,
  /jira/,
  /lucid.app/,
  /schwab.com/,
  /etrade.com/,
  /augmentcode/,
  /codecov.io/,

  // sennder
  /atlassian/,
  /slack/,
  /datadog/,
  /aws.com/,
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
];

if (!isWeekend) {
  // Local URLs, GitHub
  workURLs.push(
    /localhost/,
    /127.0.0.1/,
    /0.0.0.0/,
    /github.com/,
    /go.dev/,
    /golang/
  );
}

// https://github.com/johnste/finicky
export default {
  // Using the unstable browser for personal purposes, and the stable one for work
  defaultBrowser: "Brave Browser Beta",
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
    //   match: finicky.matchHostnames([/google\.(com|de|com.br|.+)$/]),
    //   url: ({ url }) => ({
    //     ...url,
    //     host: "duckduckgo.com"
    //   })
    // },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#remove-all-marketingtracking-information-from-urls
      match: ({url}) => url.search.includes("utm_"),
      url: ({url}) => {
        const search = url.search
          .split("&")
          .filter((part) => !part.startsWith("utm_"));
        return {
          ...url,
          search: search.join("&"),
        };
      },
    },
    // Remove "/files" when people insist to share links to the "Files" tab.
    // I want to read the description first, but I'm probably one of the few who cares about it.
    {
      match: ({url}) =>
        url.host === "github.com" && url.pathname.endsWith("/files"),
      url: ({url}) => ({
        ...url,
        pathname: url.pathname.replace(/\/files$/, ""),
      }),
    },
    {
      match: ({url}) => url.host.includes("doordash-int.com"),
      url: ({url}) => ({
        ...url,
        host: url.host.replace("doordash-int.com", "doordash.team"),
      }),
    },
  ],
  handlers: [
    {
      // Add this query string parameter to a work URL to open it in the personal browser
      match: ({url}) => url.search.includes(["personal"]),
      browser: "Brave Browser Beta",
    },
    {
      match: workURLs,
      browser: "Google Chrome",
    },
    {
      match: finicky.matchHostnames([
        /eatfirst\.(ninja|com)$/,
        "trello.com",
        "meet.google.com",
        "force.com",
        /.*atlassian\.(com|net)$/,
        /.*atl-paas.net/,
      ]),
      browser: "Google Chrome",
    },
    // Work parameters on the query string
    {
      match: ({url}) => url.search.includes(["wolt", "sennder", "eatfirst"]),
      browser: "Google Chrome",
    },
    // Work apps
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#matching-an-array-of-multiple-apps
      // https://github.com/johnste/finicky#advanced-usage
      // https://github.com/johnste/finicky/wiki/Configuration#parameters
      match: ({opener}) => opener.bundleId === "com.tinyspeck.slackmacgap",
      browser: "Google Chrome",
    },
    {
      // https://github.com/johnste/finicky/wiki/Configuration-ideas#open-zoom-links-in-zoom-app
      match: /zoom.us\/j\//,
      browser: "us.zoom.xos",
    },
  ],
};
// For more examples, see the Finicky github page https://github.com/johnste/finicky
