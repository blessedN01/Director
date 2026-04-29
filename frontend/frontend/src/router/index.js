import { createRouter, createWebHistory } from "vue-router";
import DefaultView from "../views/DefaultView.vue";
import DashboardView from "../views/DashboardView.vue";
import CollectionsView from "../views/CollectionsView.vue";
import CollectionDetailView from "../views/CollectionDetailView.vue";
import VideoEditorView from "../views/VideoEditorView.vue";
import SearchView from "../views/SearchView.vue";
import GenerationView from "../views/GenerationView.vue";
import SettingsView from "../views/SettingsView.vue";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: DashboardView,
  },
  {
    path: "/chat",
    name: "Chat",
    component: DefaultView,
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: DashboardView,
  },
  {
    path: "/collections",
    name: "Collections",
    component: CollectionsView,
  },
  {
    path: "/collections/:id",
    name: "CollectionDetail",
    component: CollectionDetailView,
    props: true,
  },
  {
    path: "/video/:id",
    name: "VideoEditor",
    component: VideoEditorView,
    props: true,
  },
  {
    path: "/search",
    name: "Search",
    component: SearchView,
  },
  {
    path: "/generate",
    name: "Generation",
    component: GenerationView,
  },
  {
    path: "/settings",
    name: "Settings",
    component: SettingsView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
