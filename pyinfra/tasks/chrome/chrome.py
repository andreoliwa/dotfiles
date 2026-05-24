"""Chrome / Brave extensions: install browser cask then print extension URLs for manual install.

Extensions can't be installed via CLI, so the task prints each URL to stdout. The user copies
and visits them manually to click "Add to Chrome".

Set host.data.brew_variant to switch the personal/company list. Default is "company".
"""

from pyinfra.facts.server import Kernel
from pyinfra.operations import brew
from shared import make_env, shell

from pyinfra import host

_ENV = make_env()

_COMMON_URLS = [
    "https://chromewebstore.google.com/detail/bitwarden-free-password-m/nngceckbapebfimnlniiiahkandclblb",
    # Show CodeCov annotations in GitHub pull requests
    "https://chromewebstore.google.com/detail/codecov/gedikamndpbemklijjkncpnolildpbgo",
    # https://github.com/chitsaou/copy-as-markdown/
    "https://chromewebstore.google.com/detail/copy-as-markdown/fkeaekngjflipcockcnpobkpbbfbhmdn",
    "https://chromewebstore.google.com/detail/deepl-translate-and-write/cofdbpoegempjloogbagkncekinflcnj",
    # GoFullPage - Full Page Screen Capture
    "https://chromewebstore.google.com/detail/gofullpage-full-page-scre/fdpohaocaechififmbbbbbknoalclacl",
    "https://chromewebstore.google.com/detail/jsonview/chklaanhfefbnpoihckbnefhakgolnmc",
    "https://chromewebstore.google.com/detail/private-internet-access/jplnlifepflhkbkgonidnobkakhmpnmh",
    "https://chromewebstore.google.com/detail/pushbullet/chlffgpmiacpedhhbkiomidkjlcfhogd",
    "https://chromewebstore.google.com/detail/refined-github/hlepfoohegkhhmjieoechaddaejaokhf",
    "https://chromewebstore.google.com/detail/rescuetime-for-chrome-and/bdakmnplckeopfghnlpocafcepegjeap/related",
    "https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo",
    "https://chromewebstore.google.com/detail/url-shortener-for-amazon/ipafcflbnpkfahilfblbenfabkoaaiid",
]

_PERSONAL_URLS = [
    "https://chromewebstore.google.com/detail/bitly-short-links-and-qr/iabeihobmhlgpkcgjiloemdbofjbdcic",
    "https://chromewebstore.google.com/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi",
    # https://github.com/DIYgod/RSSHub-Radar
    "https://chromewebstore.google.com/detail/rsshub-radar/kefjpfngnndepjbopdmoebkipbgkggaa",
    "https://chromewebstore.google.com/detail/traktflix/ehlckfimahifadnbecobagimllmbdmde",
    "https://chromewebstore.google.com/detail/trim-imdb-ratings-on-netf/lpgajkhkagnpdjklmpgjeplmgffnhhjj",
    "https://chromewebstore.google.com/detail/web-scrobbler/hhinaapppaileiechjoiifaancjggfjm",
]

# Chrome needs specific extensions to (poorly) mimic Brave's privacy features.
_COMPANY_URLS = [
    "https://chromewebstore.google.com/detail/adblocker-ultimate/ohahllgiabjaoigichmmfljhkcfikeof",
    "https://chromewebstore.google.com/detail/auto-history-wipe/amndpakmdficmebaknminpdbgdccfkjn",
]

# Extensions to remove (no CLI to uninstall; manual cleanup reference list).
_REMOVE_URLS = [
    "https://chromewebstore.google.com/detail/grammarly-for-chrome/kbfnbcaeplbcioakkpcpgfkobkghlhen",
    # GraphQL
    "https://chromewebstore.google.com/detail/graphql-developer-tools/hflnkihcpgldmkepajmpooacmmhglpff",
    "https://chromewebstore.google.com/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd",
    "https://chromewebstore.google.com/detail/mate-translate-%E2%80%93-translat/ihmgiclibbndffejedjimfjmfoabpcke",
    "https://chromewebstore.google.com/detail/raindropio/ldgfbffkinooeloadekpmfoklnobpien",
    "https://chromewebstore.google.com/detail/take-webpage-screenshots/mcbpblocgmgfnpjjppndjkmgjaogfceg",
    "https://chromewebstore.google.com/detail/todoist-for-chrome/jldhpllghnbhlbpcmnajkpdmadaolakh",
    "https://chromewebstore.google.com/detail/todoist-for-gmail/clgenfnodoocmhnlnpknojdbjjnmecff",
    "https://chromewebstore.google.com/detail/toggl-button-productivity/oejgccbfbmkkpaidnkphaiaecficdnfn",
    # https://github.com/vuejs/vue-devtools
    "https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd",
]

if host.get_fact(Kernel) == "Darwin":
    _variant = host.data.get("brew_variant", "company")
    if _variant == "company":
        brew.cask(
            name="Install google-chrome",
            src="google-chrome",
        )
    _urls = _COMMON_URLS + (_PERSONAL_URLS if _variant == "personal" else _COMPANY_URLS)

    for _url in _urls:
        shell(
            name=f"chrome extension: {_url}",
            commands=[f"echo '  {_url}'"],
            _env=_ENV,
            _ignore_errors=True,
        )
