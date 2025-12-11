// TODO: is there a way to match handlers conditionally? e.g.: only when Slack is open
const today = new Date();
const dayOfWeek = today.getDay();
const isWeekend = dayOfWeek === 6 || dayOfWeek === 0;

// Work URLs
// Match any part of the URL with the regexes below
var workURLs = [
  // keep-sorted start
  /@wolt/,
  /AccountChooser/,
  /accounts.google.com/,
  /adp.com/,
  /adyen/,
  /algolia/,
  /amazon.com/,
  /apache/,
  /asana.com/,
  /atlassian/,
  /augmentcode/,
  /aws.com/,
  /awsapps.com/,
  /b2bfood.group/,
  /baeldung/,
  /caterdesk/,
  /caterwings/,
  /chatgpt/,
  /chime.aws/,
  /cloudflare/,
  /codecov.io/,
  /confluentinc/,
  /copilot/,
  /creditornot/,
  /credorax/,
  /cuckooworkout/,
  /cursor./,
  /daas/,
  /dashlane/,
  /datadog/,
  /docs.google.com/,
  /doordash/,
  /drive.google.com/,
  /eatfirst/,
  /etrade.com/,
  /event.on24.com/,
  /figma/,
  /finaro/,
  /github.com/,
  /go.dev/,
  /golang/,
  /google.zoom/,
  /gradle/,
  /grafana/,
  /invisionapp.com/,
  /java.com/,
  /java.net/,
  /jenkins/,
  /jetbrains.com/,
  /jfrog/,
  /jira/,
  /jooq.org/,
  /k8s/,
  /kotlin/,
  /kreya/,
  /ktlint/,
  /kube/,
  /lemoncat/,
  /liveshare/,
  /lucid.app/,
  /makeeathappen/,
  /martinfowler/,
  /maven/,
  /miro.com/,
  /mvn/,
  /newrelic/,
  /okta/,
  /openai/,
  /ops.wolt/,
  /orderin/,
  /oreilly/,
  /pardot.com/,
  /phrase.com/,
  /planitpoker/,
  /postman.com/,
  /protocol-buffers/,
  /retrium.com/,
  /salesforce/,
  /scalyr/,
  /schwab.com/,
  /sentry.io/,
  /slack/,
  /sli.do/,
  /smartrecruiters.com/,
  /snowflake.com/,
  /tailscale/,
  /terraform/,
  /thoughtworks/,
  /vipps/,
  /wo.lt/,
  /wolt\./,
  /woltapi/,
  /woltapp/,
  /workday/,
  /zulip/,
  // keep-sorted end
];

if (!isWeekend) {
  // Local URLs, GitHub
  workURLs.push(
    /localhost/,
    /127.0.0.1/,
    /0.0.0.0/,
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
    // Remove "/files" when people insist on sharing links to the "Files" tab. Except when there is an anchor after it.
    // I want to read the description first, but I'm probably one of the few who cares about it.
    {
      match: ({url}) =>
        url.host === "github.com" && url.pathname.endsWith("/files") && !url.hash,
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
