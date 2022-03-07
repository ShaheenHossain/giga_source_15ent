/** @giga-module **/

import { makeEnv, startServices } from "./env";
import { legacySetupProm } from "./legacy/legacy_setup";
import { mapLegacyEnvToWowlEnv } from "./legacy/utils";
import { processTemplates } from "./core/assets";
import { session } from "@web/session";

const { mount, utils } = owl;
const { whenReady } = utils;

/**
 * Function to start a webclient.
 * It is used both in community and enterprise in main.js.
 * It's meant to be webclient flexible so we can have a subclass of
 * webclient in enterprise with added features.
 *
 * @param {owl.Component} Webclient
 */
export async function startWebClient(Webclient) {
    giga.info = {
        db: session.db,
        server_version: session.server_version,
        server_version_info: session.server_version_info,
        isEnterprise: session.server_version_info.slice(-1)[0] === "e",
    };
    giga.isReady = false;

    // setup environment
    const env = makeEnv();
    const [, templates] = await Promise.all([
        startServices(env),
        giga.loadTemplatesPromise.then(processTemplates),
    ]);
    env.qweb.addTemplates(templates);

    // start web client
    await whenReady();
    const legacyEnv = await legacySetupProm;
    mapLegacyEnvToWowlEnv(legacyEnv, env);
    const root = await mount(Webclient, { env, target: document.body, position: "self" });
    // delete giga.debug; // FIXME: some legacy code rely on this
    giga.__WOWL_DEBUG__ = { root };
    giga.isReady = true;
}
